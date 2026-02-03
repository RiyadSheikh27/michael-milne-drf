from django.urls import path
from .views import *

urlpatterns = [
    path('property/', PropertyListCreateAPIView.as_view(), name='property-list-create'),
    path('property/featured/', FeaturedPropertiesAPIView.as_view(), name='property-featured'),
    path('property/<slug:slug>/', PropertyDetailAPIView.as_view(), name='property-detail'),
    path('property/qr-code/<slug:slug>/', PropertyQRCodeAPIView.as_view(), name='property-qr-code'),
    path('property/bookmarks/list/', BookmarkListCreateAPIView.as_view(), name='bookmark-list-create'),
    path('property/bookmarks/<uuid:pk>/', BookmarkDetailAPIView.as_view(), name='bookmark-detail'),
    path('property/inspections/list/', InspectionListCreateAPIView.as_view(), name='inspection-list-create'),
    path('property/inspections/<uuid:pk>/', InspectionDetailAPIView.as_view(), name='inspection-detail'),
    path('property/statistics/user/', UserStatisticsAPIView.as_view(), name='user-statistics'),
]