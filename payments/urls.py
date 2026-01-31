from django.urls import path
from .views import (
    PropertyUnlockCreateCheckoutAPIView,
    PropertyPaymentSuccessAPIView,
    PropertyPaymentCancelAPIView,
    StripeWebhookAPIView,
    MyUnlockedPropertiesAPIView
)

urlpatterns = [
    path('properties/<slug:slug>/unlock/', PropertyUnlockCreateCheckoutAPIView.as_view(), name='property-unlock'),
    path('properties/<slug:slug>/payment-success/', PropertyPaymentSuccessAPIView.as_view(), name='payment-success'),
    path('properties/<slug:slug>/payment-cancel/', PropertyPaymentCancelAPIView.as_view(), name='payment-cancel'),
    path('webhooks/stripe/', StripeWebhookAPIView.as_view(), name='stripe-webhook'),
    path('my-unlocked-properties/', MyUnlockedPropertiesAPIView.as_view(), name='my-unlocked-properties'),
]