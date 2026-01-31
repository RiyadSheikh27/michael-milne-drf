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

stripe.api_key = settings.STRIPE_SECRET_KEY

"""Create your views here."""

class PropertyUnlockCreateCheckoutAPIView(CustomResponseMixin, APIView):
    """Create a checkout session for property unlock"""
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        """Create Stripe checkout session"""
        try:
            property_obj = get_object_or_404(Property, slug=slug)
            
            """Check if already unlocked"""
            if property_obj.is_unlocked_by(request.user):
                return self.error_response(
                    message="Property already unlocked",
                    errors="You already have access to this property",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            settings_obj = SystemSettings.get_settings()
            unlock_price = settings_obj.property_unlock_price

            success_url = request.build_absolute_uri(
                f'/api/v1/payments/properties/{slug}/payment-success/'
            ) + '?session_id={CHECKOUT_SESSION_ID}'
            
            cancel_url = request.build_absolute_uri(
                f'/api/v1/payments/properties/{slug}/payment-cancel/'
            )

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': int(unlock_price * 100),
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
                client_reference_id=f"{request.user.id}:{property_obj.id}",
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
                message="Checkout session created successfully",
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
                message="Payment gateway error",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        except Exception as e:
            return self.error_response(
                message="An error occurred",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PropertyPaymentSuccessAPIView(CustomResponseMixin, APIView):
    """GET: Handle successful payment redirect"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, slug):
        session_id = request.GET.get('session_id')

        if not session_id:
            return self.error_response(
                message="Session ID is required",
                errors="Missing session_id parameter",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            unlock = PropertyUnlock.objects.get(
                stripe_checkout_session_id=session_id,
                user=request.user
            )
            
            if unlock.payment_status == 'succeeded':
                return self.success_response(
                    message="Payment successful",
                    data={
                        'property_slug': unlock.property.slug,
                        'property_name': unlock.property.propertyName,
                        'unlocked': True,
                        'redirect_to': f'/api/properties/{unlock.property.slug}/'
                    }
                )
            return self.success_response(
                message="Payment is being processed",
                data={
                    'property_slug': unlock.property.slug,
                    'property_name': unlock.property.propertyName,
                    'status': unlock.payment_status,
                    'message': 'Payment verification in progress'
                }
            )
        
        except PropertyUnlock.DoesNotExist:
            return self.error_response(
                message="Payment session not found",
                errors="Invalid session ID",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
class PropertyPaymentCancelAPIView(CustomResponseMixin, APIView):
    """Handle cancelled payment"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, slug):
        property_obj = get_object_or_404(Property, slug=slug)
        
        return self.success_response(
            message="Payment cancelled",
            data={
                'property_slug': property_obj.slug,
                'property_name': property_obj.propertyName,
                'cancelled': True,
                'message': 'Payment cancelled. Try again anytime.',
                'retry_url': f'/api/payments/properties/{slug}/unlock/'
            }
        )

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookAPIView(APIView):
    """Handle Stripe webhooks"""
    
    permission_classes = []
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)
        
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
        try:
            unlock = PropertyUnlock.objects.get(
                stripe_checkout_session_id=session['id']
            )
            unlock.stripe_payment_intent_id = session.get('payment_intent')
            unlock.payment_status = 'succeeded'
            unlock.unlocked_at = timezone.now()
            unlock.save()
            
            print(f"Unlocked: {unlock.property.propertyName} for {unlock.user.username}")
        except PropertyUnlock.DoesNotExist:
            print(f"Unlock not found: {session['id']}")
    
    def _handle_payment_succeeded(self, payment_intent):
        try:
            unlock = PropertyUnlock.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            if unlock.payment_status != 'succeeded':
                unlock.payment_status = 'succeeded'
                unlock.unlocked_at = timezone.now()
                unlock.save()
                print(f"Payment confirmed: {unlock.property.propertyName}")
        except PropertyUnlock.DoesNotExist:
            print(f"Unlock not found for payment: {payment_intent['id']}")
    
    def _handle_payment_failed(self, payment_intent):
        try:
            unlock = PropertyUnlock.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            unlock.payment_status = 'failed'
            unlock.save()
            print(f"Payment failed: {unlock.property.propertyName}")
        except PropertyUnlock.DoesNotExist:
            print(f"Unlock not found: {payment_intent['id']}")

class MyUnlockedPropertiesAPIView(CustomResponseMixin, APIView):
    """GET: List all unlocked properties for current user"""
    
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

