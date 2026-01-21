from django.db import models
from django.contrib.auth import get_user_model
import uuid

user = get_user_model()

"""Create your models here."""
class TimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Property(TimeStampedModel):
    owner = models.ForeignKey(user, on_delete=models.CASCADE, related_name='properties')
    propertyName = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    propertyAddress = models.CharField(max_length=255)
    propertyType = models.CharField(max_length=255)

    propertyBedrooms = models.CharField(max_length=255, null=True, blank=True)
    propertyBathrooms = models.CharField(max_length=255, null=True, blank=True)
    propertyParking = models.CharField(max_length=255, null=True, blank=True)
    propertyBuildYear = models.CharField(max_length=255, null=True, blank=True)

    propertyHasPool = models.BooleanField(default=False)
    propertyIsStrataProperty = models.BooleanField(default=False)

    propertyFeatureImage = models.ImageField(upload_to='property_feature_images/')
    propertyBuiltIn = models.CharField(max_length=100, null=True, blank=True)

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
            self.slug = slugify(self.propertyName)
        super().save(*args, **kwargs)

    def increment_views(self):
        self.total_views += 1
        self.save(update_fields=['total_views'])

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
        return self.propertyHasPool + self.propertyIsStrataProperty

class PropertyImage(TimeStampedModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Property Image'
        verbose_name_plural = 'Property Images'
        ordering = ['-createdAt']

    def __str__(self):
        return f"Image for {self.property.propertyName}"

class PropertyInspectionReport(TimeStampedModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inspection_reports')
    report = models.FileField(upload_to='property_inspection_reports/', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Property Inspection Report'
        verbose_name_plural = 'Property Inspection Reports'
        ordering = ['-createdAt']

    def __str__(self):
        return f"Inspection Report for {self.property.propertyName}"

class PropertyOptionalReport(TimeStampedModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='optional_reports')
    report = models.FileField(upload_to='property_optional_reports/', null=True, blank=True)
    
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
        return f"Feature for {self.property.propertyName}"
