from rest_framework import serializers
from payments.models import PropertyUnlock

class PropertyUnlockSerializer(serializers.ModelSerializer):
    """Serializer for property unlock records"""
    
    property_name = serializers.CharField(source='property.propertyName', read_only=True)
    property_slug = serializers.CharField(source='property.slug', read_only=True)
    
    class Meta:
        model = PropertyUnlock
        fields = [
            'id',
            'property_name',
            'property_slug',
            'amount_paid',
            'currency',
            'payment_status',
            'unlocked_at',
            'createdAt',
        ]