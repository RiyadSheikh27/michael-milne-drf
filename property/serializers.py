from rest_framework import serializers
from .models import *
from payments.models import SystemSettings

"""Start of Serializer Section"""

class PropertyFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyFeature
        fields = ['id', 'feature', 'createdAt', 'updatedAt']
        read_only_fields = ['id', 'createdAt', 'updatedAt']

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'createdAt', 'updatedAt']
        read_only_fields = ['id', 'createdAt', 'updatedAt']

class PropertyInspectionReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyInspectionReport
        fields = ['id', 'report', 'createdAt', 'updatedAt']
        read_only_fields = ['id', 'createdAt', 'updatedAt']
    
class PropertyOptionalReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyOptionalReport
        fields = ['id', 'report', 'createdAt', 'updatedAt']
        read_only_fields = ['id', 'createdAt', 'updatedAt']

class PropertyCreateUpdateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False, allow_empty=True)
    inspection_reports = serializers.ListField(child=serializers.FileField(), write_only=True, required=False, allow_empty=True)
    optional_reports = serializers.ListField(child=serializers.FileField(), write_only=True, required=False, allow_empty=True)
    features = serializers.ListField(child=serializers.CharField(), write_only=True, required=False, allow_empty=True)
    
    class Meta:
        model = Property
        fields = ['id', 'propertyName', 'propertyAddress', 'propertyType', 'propertyBathrooms', 'propertyBedrooms', 'propertyParking', 'propertyBuildYear', 'propertyHasPool', 'propertyIsStrataProperty', 'status', 'propertyFeatureImage', 'images', 'inspection_reports', 'optional_reports', 'features', 'createdAt', 'updatedAt']
        read_only_fields = ['id', 'createdAt', 'updatedAt']

    def validate_images(self, value):
        """Validate maximum number of images"""
        if len(value) > 10:
            raise serializers.ValidationError("Maximum 10 images allowed.")
        return value

    def validate_inspection_reports(self, value):
        """Validate maximum number of inspection reports"""
        if len(value) > 5:
            raise serializers.ValidationError("Maximum 5 inspection reports allowed.")
        return value
    
    def validate_optional_reports(self, value):
        """Validate maximum number of optional reports"""
        if len(value) > 5:
            raise serializers.ValidationError("Maximum 5 optional reports allowed.")
        return value
    
    def validate_features(self, value):
        """Validate maximum number of features"""
        if len(value) > 20:
            raise serializers.ValidationError("Maximum 20 features allowed.")
        return value

class PropertyListSerializer(serializers.ModelSerializer):
    """Serializer for property list view"""
    unlock_price = serializers.SerializerMethodField()
    is_unlocked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id',
            'slug',
            'propertyName',
            'propertyAddress',
            'status',
            'propertyFeatureImage',
            'total_inspection_reports',
            'total_optional_reports',
            'propertyBedrooms',
            'propertyBathrooms',
            'propertyParking',
            'propertyBuildYear',
            'unlock_price',
            'is_unlocked',
            'is_bookmarked',
            'createdAt',
            'updatedAt'
        ]

    def get_unlock_price(self, obj):
        """Get the unlock price from system settings"""
        settings = SystemSettings.get_settings()
        return float(settings.property_unlock_price)

    def get_is_unlocked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_unlocked_by(request.user)
        return False

    def get_is_bookmarked(self, obj):
        """Check if property is bookmarked by current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Bookmark.objects.filter(user=request.user, property=obj).exists()
        return False

class PropertyDetailSerializer(serializers.ModelSerializer):
    """Serializer for property detail view with related data"""
    
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    owner_phone = serializers.CharField(source='owner.phone', read_only=True)
    owner_image = serializers.CharField(source='owner.image', read_only=True)
    owner_is_agent = serializers.BooleanField(source='owner.is_agent', read_only=True)
    
    images = PropertyImageSerializer(many=True, read_only=True)
    inspection_reports = PropertyInspectionReportSerializer(many=True, read_only=True)
    optional_reports = PropertyOptionalReportSerializer(many=True, read_only=True)
    features = PropertyFeatureSerializer(many=True, read_only=True)
    
    total_photos = serializers.IntegerField(read_only=True)
    total_inspection_reports = serializers.IntegerField(read_only=True)
    total_optional_reports = serializers.IntegerField(read_only=True)
    checkboxes_checked = serializers.IntegerField(read_only=True)
    qr_code_url = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    is_unlocked = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id',
            'slug',
            'owner_name',
            'owner_email',
            'owner_phone',
            'owner_image',
            'owner_is_agent',
            'propertyName',
            'propertyAddress',
            'propertyType',
            'propertyBedrooms',
            'propertyBathrooms',
            'propertyParking',
            'propertyBuildYear',
            'propertyHasPool',
            'propertyIsStrataProperty',
            'status',
            'is_unlocked',
            'propertyFeatureImage',
            'images',
            'inspection_reports',
            'optional_reports',
            'features',
            'total_photos',
            'total_inspection_reports',
            'total_optional_reports',
            'total_views',
            'checkboxes_checked',
            'qr_code_url',
            'is_bookmarked',
            'createdAt',
            'updatedAt',
        ]
    
    def get_qr_code_url(self, obj):
        """Generate QR code URL for property"""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/properties/{obj.slug}/')
        return None

    def get_is_bookmarked(self, obj):
        """Check if property is bookmarked by current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Bookmark.objects.filter(user=request.user, property=obj).exists()
        return False
    
    def get_is_unlocked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_unlocked_by(request.user)
        return False


class BookmarkSerializer(serializers.ModelSerializer):
    """Serializer for bookmark with property details"""
    property = PropertyListSerializer(read_only=True)
    property_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Bookmark
        fields = ['id', 'property', 'property_id', 'createdAt', 'updatedAt']
        read_only_fields = ['id', 'createdAt', 'updatedAt']
    
    def validate_property_id(self, value):
        """Validate that property exists"""
        if not Property.objects.filter(id=value).exists():
            raise serializers.ValidationError("Property does not exist.")
        return value


class InspectionSerializer(serializers.ModelSerializer):
    """Serializer for inspection booking"""
    property = PropertyListSerializer(read_only=True)
    property_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Inspection
        fields = ['id', 'property', 'property_id', 'inspection_datetime', 'createdAt', 'updatedAt']
        read_only_fields = ['id', 'createdAt', 'updatedAt']
    
    def validate_property_id(self, value):
        """Validate that property exists"""
        if not Property.objects.filter(id=value).exists():
            raise serializers.ValidationError("Property does not exist.")
        return value
    
    def validate_inspection_datetime(self, value):
        """Validate that inspection datetime is in the future"""
        from django.utils import timezone
        if value < timezone.now():
            raise serializers.ValidationError("Inspection date/time must be in the future.")
        return value


class UserStatisticsSerializer(serializers.Serializer):
    """Serializer for user statistics"""
    total_bookmarks = serializers.IntegerField()
    total_inspections = serializers.IntegerField()
    total_properties = serializers.IntegerField()
    bookmarked_properties = PropertyListSerializer(many=True)
    upcoming_inspections = InspectionSerializer(many=True)