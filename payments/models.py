from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

"""Start of models here."""

class TimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SystemSettings(models.Model):
    """Global system settings - managed from admin panel"""
    
    property_unlock_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=9.99,
        help_text="Price to unlock a single property (in USD)"
    )

    class Meta:
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'

    def __str__(self):
        return f"Unlock price: ${self.property_unlock_price}"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get or create settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

    
class PropertyUnlock(TimeStampedModel):
    """Track which users have unlocked which properties"""
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='unlocked_properties'
    )
    property = models.ForeignKey(
        "property.Property",
        on_delete=models.CASCADE,
        related_name='unlocks'
    )
    stripe_checkout_session_id = models.CharField(max_length=255, unique=True)
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)
    
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    
    unlocked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Property Unlock'
        verbose_name_plural = 'Property Unlocks'
        unique_together = ['user', 'property']
        ordering = ['-createdAt']
    
    def __str__(self):
        return f"{self.user.username} - {self.property.propertyName} ({self.payment_status})"