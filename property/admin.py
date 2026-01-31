from django.contrib import admin
from .models import (
    Property,
    PropertyImage,
    PropertyInspectionReport,
    PropertyOptionalReport,
    PropertyFeature
)

# --------------------------
# Inlines for related models (Add-only)
# --------------------------
class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    can_delete = False  # prevent deletion from Property admin

class PropertyInspectionReportInline(admin.TabularInline):
    model = PropertyInspectionReport
    extra = 1
    can_delete = False  # prevent deletion from Property admin

class PropertyOptionalReportInline(admin.TabularInline):
    model = PropertyOptionalReport
    extra = 1
    can_delete = False  # prevent deletion from Property admin

class PropertyFeatureInline(admin.TabularInline):
    model = PropertyFeature
    extra = 1
    can_delete = False  # prevent deletion from Property admin

# --------------------------
# Property Admin
# --------------------------
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = [
        'propertyName',
        'slug',
        'owner',
        'propertyType',
        'status',
        'total_views',
        'createdAt',
    ]
    list_filter = ['status', 'propertyType', 'propertyHasPool', 'propertyIsStrataProperty']
    search_fields = ['propertyName', 'slug', 'owner__username', 'propertyAddress']
    readonly_fields = ['slug', 'total_views', 'createdAt', 'updatedAt']
    inlines = [
        PropertyImageInline,
        PropertyInspectionReportInline,
        PropertyOptionalReportInline,
        PropertyFeatureInline,
    ]
    ordering = ['-createdAt']

# --------------------------
# Admin for individual models (full CRUD)
# --------------------------
@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ['property', 'image', 'createdAt']

@admin.register(PropertyInspectionReport)
class PropertyInspectionReportAdmin(admin.ModelAdmin):
    list_display = ['property', 'report', 'createdAt']

@admin.register(PropertyOptionalReport)
class PropertyOptionalReportAdmin(admin.ModelAdmin):
    list_display = ['property', 'report', 'createdAt']

@admin.register(PropertyFeature)
class PropertyFeatureAdmin(admin.ModelAdmin):
    list_display = ['feature', 'property', 'createdAt']
