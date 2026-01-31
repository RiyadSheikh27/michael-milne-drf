from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.utils.text import slugify

User = get_user_model()

"""Create your models here."""
class TimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        

class Property(TimeStampedModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    propertyName = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    propertyAddress = models.CharField(max_length=255)
    propertyType = models.CharField(max_length=255)

    propertyBedrooms = models.CharField(max_length=255, null=True, blank=True)
    propertyBathrooms = models.CharField(max_length=255, null=True, blank=True)
    propertyParking = models.CharField(max_length=255, null=True, blank=True)
    propertyBuildYear = models.CharField(max_length=255, null=True, blank=True)

    propertyHasPool = models.BooleanField(default=False)
    propertyIsStrataProperty = models.BooleanField(default=False)

    propertyFeatureImage = models.ImageField(upload_to='property_feature_images/')

    status = models.BooleanField(default=True)
    total_views = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        ordering = ['-createdAt']

    def __str__(self):
        return self.propertyName

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.propertyName)
            slug = base_slug
            counter = 1
            while Property.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def increment_views(self):
        self.total_views += 1
        self.save(update_fields=['total_views'])

    def is_unlocked_by(self, user):
        """Check if property is unlocked by user"""
        if not user.is_authenticated:
            return False
        
        """Owner can always see their own properties"""
        if self.owner == user:
            return True
        
        """Check if user has unlocked this property"""
        from payments.models import PropertyUnlock
        return PropertyUnlock.objects.filter(
            user=user,
            property=self,
            payment_status='succeeded'
        ).exists()

    @property
    def total_photos(self):
        return 1 + self.images.count()

    @property
    def total_inspection_reports(self):
        return self.inspection_reports.count()

    @property
    def total_optional_reports(self):
        return self.optional_reports.count()

    @property
    def checkboxes_checked(self):
        return int(self.propertyHasPool) + int(self.propertyIsStrataProperty)


class PropertyImage(TimeStampedModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    
    class Meta:
        verbose_name = 'Property Image'
        verbose_name_plural = 'Property Images'
        ordering = ['-createdAt']

    def __str__(self):
        return f"Image for {self.property.propertyName}"


class PropertyInspectionReport(TimeStampedModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inspection_reports')
    report = models.FileField(upload_to='property_inspection_reports/')
    
    class Meta:
        verbose_name = 'Property Inspection Report'
        verbose_name_plural = 'Property Inspection Reports'
        ordering = ['-createdAt']

    def __str__(self):
        return f"Inspection Report for {self.property.propertyName}"


class PropertyOptionalReport(TimeStampedModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='optional_reports')
    report = models.FileField(upload_to='property_optional_reports/')
    
    class Meta:
        verbose_name = 'Property Optional Report'
        verbose_name_plural = 'Property Optional Reports'
        ordering = ['-createdAt']

    def __str__(self):
        return f"Optional Report for {self.property.propertyName}"


class PropertyFeature(TimeStampedModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='features')
    feature = models.CharField(max_length=255)
    
    class Meta:
        verbose_name = 'Property Feature'
        verbose_name_plural = 'Property Features'
        ordering = ['-createdAt']

    def __str__(self):
        return f"{self.feature} - {self.property.propertyName}"