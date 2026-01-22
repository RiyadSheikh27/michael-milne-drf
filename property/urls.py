from django.urls import path
from .views import PropertyListCreateAPIView

urlpatterns = [
    path('owner/property/', PropertyListCreateAPIView.as_view(), name='property-list-create'),
]