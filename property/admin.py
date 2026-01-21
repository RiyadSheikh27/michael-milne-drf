from django.contrib import admin
from django.utils.html import format_html
from .models import *

"""----------------- INLINES -----------------"""

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ('image_tag', 'image')
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100"/>', obj.image.url)
        return "-"
    image_tag.short_description = "Preview"


class PropertyInspectionReportInline(admin.TabularInline):
    model = PropertyInspectionReport
    extra = 1
    fields = ('report',)


class PropertyOptionalReportInline(admin.TabularInline):
    model = PropertyOptionalReport
    extra = 1
    fields = ('report',)


class PropertyFeatureInline(admin.TabularInline):
    model = PropertyFeature
    extra = 1
    fields = ('feature',)


"""----------------- MAIN ADMIN -----------------"""

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        'propertyName', 'owner', 'propertyType', 'total_views',
        'propertyHasPool', 'propertyIsStrataProperty', 'status'
    )
    list_filter = ('propertyType', 'status', 'propertyHasPool', 'propertyIsStrataProperty')
    search_fields = ('propertyName', 'owner__username', 'propertyAddress')
    readonly_fields = ('slug', 'total_views')

    inlines = [
        PropertyImageInline,
        PropertyInspectionReportInline,
        PropertyOptionalReportInline,
        PropertyFeatureInline
    ]

    fieldsets = (
        ('Basic Info', {
            'fields': ('owner', 'propertyName', 'slug', 'propertyAddress', 'propertyType')
        }),
        ('Details', {
            'fields': ('propertyBedrooms', 'propertyBathrooms', 'propertyParking', 'propertyBuildYear')
        }),
        ('Features & Status', {
            'fields': ('propertyHasPool', 'propertyIsStrataProperty', 'status', 'propertyFeatureImage')
        }),
    )

    def save_model(self, request, obj, form, change):
        """Automatically assign owner if not set"""
        if not obj.owner:
            obj.owner = request.user
        super().save_model(request, obj, form, change)
