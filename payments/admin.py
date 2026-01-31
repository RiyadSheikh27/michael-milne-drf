from django.contrib import admin
from .models import SystemSettings, PropertyUnlock

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['property_unlock_price']
    
    def has_add_permission(self, request):
        return not SystemSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(PropertyUnlock)
class PropertyUnlockAdmin(admin.ModelAdmin):
    list_display = ['user', 'property', 'amount_paid', 'payment_status', 'unlocked_at', 'createdAt']
    list_filter = ['payment_status', 'createdAt']
    search_fields = ['user__username', 'property__propertyName']
    readonly_fields = ['stripe_checkout_session_id', 'stripe_payment_intent_id', 'createdAt', 'updatedAt']