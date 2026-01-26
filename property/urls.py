from django.urls import path
from .views import PropertyListCreateAPIView, PropertyDetailAPIView, PropertyQRCodeAPIView

urlpatterns = [
    path('property/', PropertyListCreateAPIView.as_view(), name='property-list-create'),
    path('property/<slug:slug>/', PropertyDetailAPIView.as_view(), name='property-detail'),
    path('property/qr-code/<slug:slug>/', PropertyQRCodeAPIView.as_view(), name='property-qr-code'),
]