from django.urls import path
from .views import *

urlpatterns = [
    path('property/', PropertyListCreateAPIView.as_view(), name='property-list-create'),
    path('property/featured/', FeaturedPropertiesAPIView.as_view(), name='property-featured'),
    path('property/<slug:slug>/', PropertyDetailAPIView.as_view(), name='property-detail'),
    path('property/qr-code/<slug:slug>/', PropertyQRCodeAPIView.as_view(), name='property-qr-code'),
]