# sitesettings/urls.py
from django.urls import path
from .views import RequestQuoteViewSet

urlpatterns = [
    path('request-quote/', RequestQuoteViewSet.as_view({'post': 'create'}), name='request-quote'),
]