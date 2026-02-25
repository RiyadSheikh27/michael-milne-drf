from .models import *
from rest_framework import serializers

class RequestQuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestQuote
        fields = "__all__"

        read_only_fields = ['id', 'email', 'createdAt', 'updatedAt']