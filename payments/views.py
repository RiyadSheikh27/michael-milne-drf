from django.shortcuts import render
from django.utils import timezone
from .models import *
from .serializers import *
from property.views import CustomResponseMixin
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from property.models import Property
from django.shortcuts import get_object_or_404
import stripe
from django.conf import settings
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import redirect

stripe.api_key = settings.STRIPE_SECRET_KEY


class PropertyUnlockCreateCheckoutAPIView(CustomResponseMixin, APIView):
    """
    API view to create a Stripe checkout session for unlocking a property.
    
    Handles the creation of a payment session and stores the pending unlock record.
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, slug):
        try:
            property_obj = get_object_or_404(Property, slug=slug)
            
            if property_obj.owner == request.user:
                return self.error_response(
                    message="Cannot unlock own property",
                    errors="You are the owner",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            if property_obj.is_unlocked_by(request.user):
                return self.error_response(
                    message="Property already unlocked",
                    errors="You already have access",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            """
            Delete any previous pending record for retry
            """
            PropertyUnlock.objects.filter(
                user=request.user,
                property=property_obj,
                payment_status='pending'
            ).delete()
            
            settings_obj = SystemSettings.get_settings()
            unlock_price = settings_obj.property_unlock_price
            
            """
            Build backend URLs for intermediate processing
            Backend will verify payment then redirect to frontend
            """
            base_url = f"{request.scheme}://{request.get_host()}"
            
            success_url = (
                f"{base_url}"
                f"/api/v1/payments/properties/{slug}/payment-success/"
                f"?session_id={{CHECKOUT_SESSION_ID}}"
            )
            cancel_url = (
                f"{base_url}"
                f"/api/v1/payments/properties/{slug}/payment-cancel/"
            )
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': int(float(unlock_price) * 100),
                            'product_data': {
                                'name': f'Unlock: {property_obj.propertyName}',
                                'description': 'Full access to property details',
                            },
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'user_id': str(request.user.id),
                    'property_id': str(property_obj.id),
                    'property_slug': property_obj.slug,
                }
            )
            
            PropertyUnlock.objects.create(
                user=request.user,
                property=property_obj,
                stripe_checkout_session_id=checkout_session.id,
                amount_paid=unlock_price,
                currency='USD',
                payment_status='pending'
            )
            
            return self.success_response(
                message="Checkout session created",
                data={
                    'checkout_url': checkout_session.url,
                    'session_id': checkout_session.id,
                    'amount': float(unlock_price),
                    'currency': 'USD',
                    'property_name': property_obj.propertyName,
                },
                status_code=status.HTTP_201_CREATED
            )
        
        except stripe.error.StripeError as e:
            return self.error_response(
                message="Stripe error",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return self.error_response(
                message="Error",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PropertyPaymentSuccessAPIView(APIView):
    """
    Handle successful payment redirect.
    
    CRITICAL: This endpoint verifies payment with Stripe and updates database
    BEFORE redirecting to frontend. This ensures payment is confirmed.
    """
    
    permission_classes = []
    authentication_classes = []
    
    def get(self, request, slug):
        session_id = request.GET.get('session_id')
        
        if not session_id:
            """
            Redirect to frontend with error
            """
            return redirect(
                f"{settings.FRONTEND_BASE_URL}/payment/error?message=session_missing"
            )
        
        try:
            stripe_session = stripe.checkout.Session.retrieve(session_id)
            if stripe_session.get('payment_status') != 'paid':
                return redirect(
                    f"{settings.FRONTEND_BASE_URL}/payment/error?message=payment_not_completed"
                )
            
            try:
                unlock = PropertyUnlock.objects.get(
                    stripe_checkout_session_id=session_id
                )
            except PropertyUnlock.DoesNotExist:
                return redirect(
                    f"{settings.FRONTEND_BASE_URL}/payment/error?message=unlock_not_found"
                )
            
            if unlock.payment_status != 'succeeded':
                unlock.stripe_payment_intent_id = stripe_session.get('payment_intent')
                unlock.payment_status = 'succeeded'
                unlock.unlocked_at = timezone.now()
                unlock.save()
            
            return redirect(
                f"{settings.FRONTEND_BASE_URL}/property_details/{slug}/"
            )
        
        except stripe.error.StripeError as e:
            """
            Stripe API error
            """
            return redirect(
                f"{settings.FRONTEND_BASE_URL}/payment/error?message=stripe_error"
            )
        
        except Exception as e:
            """
            Any other error
            """
            import traceback
            traceback.print_exc()
            return redirect(
                f"{settings.FRONTEND_BASE_URL}/payment/error?message=server_error"
            )


class PropertyPaymentCancelAPIView(APIView):
    """
    Handle cancelled payment.
    
    Redirects to frontend with cancellation info.
    """
    
    permission_classes = []
    authentication_classes = []
    
    def get(self, request, slug):
        try:
            property_obj = get_object_or_404(Property, slug=slug)
            
            """
            Redirect to frontend with cancellation info
            """
            return redirect(
                f"{settings.FRONTEND_BASE_URL}/payment/cancelled"
                f"?property_slug={slug}"
                f"&property_name={property_obj.propertyName}"
            )
        except Exception as e:
            return redirect(
                f"{settings.FRONTEND_BASE_URL}/payment/error?message=property_not_found"
            )


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookAPIView(APIView):
    """
    Handle Stripe webhooks.
    
    This provides a backup confirmation mechanism.
    The success endpoint confirms payment first, but webhooks
    provide additional reliability for delayed confirmations.
    """
    
    permission_classes = []
    authentication_classes = []
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        """
        Check if webhook secret exists
        """
        if not settings.STRIPE_WEBHOOK_SECRET:
            return HttpResponse(status=400)
        
        """
        Check if signature exists
        """
        if not sig_header:
            return HttpResponse(status=400)
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            
        except ValueError as e:
            return HttpResponse(status=400)
            
        except stripe.error.SignatureVerificationError as e:
            return HttpResponse(status=400)
        
        """
        Handle events
        """
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            self._handle_checkout_completed(session)
        
        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self._handle_payment_succeeded(payment_intent)
        
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            self._handle_payment_failed(payment_intent)
        
        return HttpResponse(status=200)
    
    def _handle_checkout_completed(self, session):
        """
        Handle completed checkout session.
        
        Updates the unlock record to succeeded status.
        This is a backup - the success endpoint should already handle this.
        """
        try:
            session_id = session['id']
            
            unlock = PropertyUnlock.objects.get(
                stripe_checkout_session_id=session_id
            )
            
            """
            Only update if not already succeeded
            """
            if unlock.payment_status != 'succeeded':
                unlock.stripe_payment_intent_id = session.get('payment_intent')
                unlock.payment_status = 'succeeded'
                unlock.unlocked_at = timezone.now()
                unlock.save()
            
        except PropertyUnlock.DoesNotExist:
            pass
        
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def _handle_payment_succeeded(self, payment_intent):
        """
        Handle successful payment intent.
        
        Confirms payment success and updates unlock status.
        """
        try:
            unlock = PropertyUnlock.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            if unlock.payment_status != 'succeeded':
                unlock.payment_status = 'succeeded'
                unlock.unlocked_at = timezone.now()
                unlock.save()
        except PropertyUnlock.DoesNotExist:
            pass
    
    def _handle_payment_failed(self, payment_intent):
        """
        Handle failed payment intent.
        
        Updates unlock record to failed status.
        """
        try:
            unlock = PropertyUnlock.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            unlock.payment_status = 'failed'
            unlock.save()
        except PropertyUnlock.DoesNotExist:
            pass


class MyUnlockedPropertiesAPIView(CustomResponseMixin, APIView):
    """
    List all unlocked properties for current user.
    
    Returns a list of properties the user has successfully unlocked.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            unlocks = PropertyUnlock.objects.filter(
                user=request.user,
                payment_status='succeeded'
            ).select_related('property')
            
            serializer = PropertyUnlockSerializer(unlocks, many=True)
            
            return self.success_response(
                message="Unlocked properties retrieved successfully",
                data=serializer.data
            )
        
        except Exception as e:
            return self.error_response(
                message="An error occurred",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )