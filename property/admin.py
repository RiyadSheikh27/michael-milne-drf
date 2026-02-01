from django.contrib import admin
from .models import (
    Property,
    PropertyImage,
    PropertyInspectionReport,
    PropertyOptionalReport,
    PropertyFeature,
    Bookmark,
    Inspection
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
        'unlocked',
        'total_views',
        'total_bookmarks',
        'total_inspections',
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

    def unlocked(self, obj):
        # No request.user in admin, show owner perspective
        return obj.is_unlocked_by(obj.owner)

    unlocked.boolean = True
    unlocked.short_description = 'Unlocked'

    def total_bookmarks(self, obj):
        """Display total bookmarks for this property"""
        return obj.bookmarks.count()
    
    total_bookmarks.short_description = 'Bookmarks'

    def total_inspections(self, obj):
        """Display total inspections booked for this property"""
        return obj.inspections.count()
    
    total_inspections.short_description = 'Inspections'

# --------------------------
# Admin for individual models (full CRUD)
# --------------------------
@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ['property', 'image', 'createdAt']
    list_filter = ['createdAt']
    search_fields = ['property__propertyName']
    readonly_fields = ['id', 'createdAt', 'updatedAt']

@admin.register(PropertyInspectionReport)
class PropertyInspectionReportAdmin(admin.ModelAdmin):
    list_display = ['property', 'report', 'createdAt']
    list_filter = ['createdAt']
    search_fields = ['property__propertyName']
    readonly_fields = ['id', 'createdAt', 'updatedAt']

@admin.register(PropertyOptionalReport)
class PropertyOptionalReportAdmin(admin.ModelAdmin):
    list_display = ['property', 'report', 'createdAt']
    list_filter = ['createdAt']
    search_fields = ['property__propertyName']
    readonly_fields = ['id', 'createdAt', 'updatedAt']

@admin.register(PropertyFeature)
class PropertyFeatureAdmin(admin.ModelAdmin):
    list_display = ['feature', 'property', 'createdAt']
    list_filter = ['createdAt']
    search_fields = ['feature', 'property__propertyName']
    readonly_fields = ['id', 'createdAt', 'updatedAt']

# --------------------------
# New Models Admin
# --------------------------
@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'property', 'createdAt']
    list_filter = ['createdAt']
    search_fields = ['user__email', 'user__username', 'property__propertyName']
    readonly_fields = ['id', 'createdAt', 'updatedAt']
    ordering = ['-createdAt']
    
    fieldsets = (
        ('Bookmark Information', {
            'fields': ('user', 'property')
        }),
        ('Metadata', {
            'fields': ('id', 'createdAt', 'updatedAt'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'property', 'inspection_datetime', 'is_upcoming', 'createdAt']
    list_filter = ['inspection_datetime', 'createdAt']
    search_fields = ['user__email', 'user__username', 'property__propertyName']
    readonly_fields = ['id', 'createdAt', 'updatedAt']
    ordering = ['-inspection_datetime']
    date_hierarchy = 'inspection_datetime'
    
    fieldsets = (
        ('Inspection Information', {
            'fields': ('user', 'property', 'inspection_datetime')
        }),
        ('Metadata', {
            'fields': ('id', 'createdAt', 'updatedAt'),
            'classes': ('collapse',)
        }),
    )

    def is_upcoming(self, obj):
        """Check if inspection is in the future"""
        from django.utils import timezone
        return obj.inspection_datetime > timezone.now()
    
    is_upcoming.boolean = True
    is_upcoming.short_description = 'Upcoming'