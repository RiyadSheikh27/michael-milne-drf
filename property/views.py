import qrcode
import base64
from io import BytesIO
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.views import APIView
from .models import *
from .serializers import *
from utils.permissions import IsAdmin, IsAdminOrReadOnly, IsOwnerOrReadOnly
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from rest_framework.permissions import SAFE_METHODS
from django.utils import timezone


"""Start of views for property section"""

class CustomResponseMixin:
    def success_response(self, message, data=None, status_code=status.HTTP_200_OK):
        """Standard Success Response"""
        return Response(
            {
                "success": True,
                "messgae": message,
                "data": data
            }, status=status_code
        )

    def error_response(self, message, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        """Standard Error Response"""
        return Response(
            {
                "success": False,
                "message": message,
                "data": None,
                "errors": errors
            }, status=status_code
        )

class PropertyListCreateAPIView(CustomResponseMixin, APIView):
    """GET All Active Properties || Create Property"""
    permission_classes = [IsAuthenticated]
    serializer_class = PropertyCreateUpdateSerializer

    def get(self, request):
        try:
            user = request.user

            if user.role == 'owner':
                """OWNER → only own properties (active + inactive)"""
                properties = Property.objects.filter(
                    owner=user
                ).select_related('owner')

            else:
                """BUYER → all active properties"""
                properties = Property.objects.filter(
                    status=True
                ).select_related('owner')

            property_type = request.GET.get('property_type')
            if property_type:
                properties = properties.filter(propertyType__iexact=property_type)

            bedrooms = request.GET.get('bedrooms')
            if bedrooms:
                properties = properties.filter(propertyBedrooms=bedrooms)

            bathrooms = request.GET.get('bathrooms')
            if bathrooms:
                properties = properties.filter(propertyBathrooms=bathrooms)

            parking = request.GET.get('parking')
            if parking:
                properties = properties.filter(propertyParking=parking)

            has_pool = request.GET.get('has_pool')
            if has_pool is not None:
                pool_value = has_pool.lower() == 'true'
                properties = properties.filter(propertyHasPool=pool_value)

            is_strata = request.GET.get('is_strata')
            if is_strata is not None:
                strata_value = is_strata.lower() == 'true'
                properties = properties.filter(propertyIsStrataProperty=strata_value)

                
            search = request.GET.get('search')
            if search:
                properties = properties.filter(
                    models.Q(propertyName__icontains=search) |
                    models.Q(propertyAddress__icontains=search)
                )

            serializers = PropertyListSerializer(properties, many=True, context={'request': request})

            return self.success_response(
                message="Properties retrieved successfully",
                data = serializers.data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return self.error_response(
                message="An error occured while retrivering properties",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @transaction.atomic
    def post(self, request):
        """Create a new property"""
        serializer = PropertyCreateUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return self.error_response(
                message="Validation failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            validated_data = serializer.validated_data
            
            """Extract file lists and features"""
            images = validated_data.pop('images', [])
            inspection_reports = validated_data.pop('inspection_reports', [])
            optional_reports = validated_data.pop('optional_reports', [])
            features = validated_data.pop('features', [])
            
            """Create property with owner"""
            property_obj = Property.objects.create(
                owner=request.user,
                **validated_data
            )
            
            """Bulk create related images"""
            if images:
                PropertyImage.objects.bulk_create([
                    PropertyImage(property=property_obj, image=img)
                    for img in images
                ])
            
            """Bulk create inspection reports"""
            if inspection_reports:
                PropertyInspectionReport.objects.bulk_create([
                    PropertyInspectionReport(property=property_obj, report=report)
                    for report in inspection_reports
                ])
            
            """Bulk create optional reports"""
            if optional_reports:
                PropertyOptionalReport.objects.bulk_create([
                    PropertyOptionalReport(property=property_obj, report=report)
                    for report in optional_reports
                ])
            
            """Bulk create features"""
            if features:
                PropertyFeature.objects.bulk_create([
                    PropertyFeature(property=property_obj, feature=feature)
                    for feature in features
                ])
            
            """Serialize response"""
            response_data = PropertyDetailSerializer(
                property_obj,
                context={'request': request}
            ).data
            
            return self.success_response(
                message="Property created successfully",
                data=response_data,
                status_code=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            return self.error_response(
                message="An error occurred while creating the property",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PropertyDetailAPIView(CustomResponseMixin, APIView):
    """
    GET: Retrieve property details by slug (increments view count)
    PATCH: Partially update property (owner only)
    DELETE: Delete property (owner only)
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_object(self, slug):
        """Get property object by slug"""
        return get_object_or_404(Property, slug=slug)
    
    def get(self, request, slug):
        """Retrieve property details and increment view count"""
        try:
            property_obj = self.get_object(slug)


            settings_obj = SystemSettings.get_settings()

            
            """Check permission"""
            self.check_object_permissions(request, property_obj)
            
            """Increment view count (only for non-owners)"""
            if request.user != property_obj.owner:
                property_obj.increment_views()
            
            serializer = PropertyDetailSerializer(
                property_obj,
                context={'request': request}
            )
            
            return self.success_response(
                message="Property retrieved successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        
        except Exception as e:
            return self.error_response(
                message="An error occurred while retrieving the property",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @transaction.atomic
    def patch(self, request, slug):
        """Partially update property"""
        property_obj = self.get_object(slug)
        
        """Check permission"""
        self.check_object_permissions(request, property_obj)
        
        serializer = PropertyCreateUpdateSerializer(
            data=request.data,
            partial=True
        )
        
        if not serializer.is_valid():
            return self.error_response(
                message="Validation failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            validated_data = serializer.validated_data
            
            """Extract file lists and features"""
            images = validated_data.pop('images', None)
            inspection_reports = validated_data.pop('inspection_reports', None)
            optional_reports = validated_data.pop('optional_reports', None)
            features = validated_data.pop('features', None)
            
            """Update basic property fields"""
            for attr, value in validated_data.items():
                setattr(property_obj, attr, value)
            
            property_obj.save()
            
            """Update images (if provided, replace all)"""
            if images is not None:
                property_obj.images.all().delete()
                PropertyImage.objects.bulk_create([
                    PropertyImage(property=property_obj, image=img)
                    for img in images
                ])
            
            """Update inspection reports (if provided, replace all)"""
            if inspection_reports is not None:
                property_obj.inspection_reports.all().delete()
                PropertyInspectionReport.objects.bulk_create([
                    PropertyInspectionReport(property=property_obj, report=report)
                    for report in inspection_reports
                ])
            
            """Update optional reports (if provided, replace all)"""
            if optional_reports is not None:
                property_obj.optional_reports.all().delete()
                PropertyOptionalReport.objects.bulk_create([
                    PropertyOptionalReport(property=property_obj, report=report)
                    for report in optional_reports
                ])
            
            """Update features (if provided, replace all)"""
            if features is not None:
                property_obj.features.all().delete()
                PropertyFeature.objects.bulk_create([
                    PropertyFeature(property=property_obj, feature=feature)
                    for feature in features
                ])
            
            """Serialize response"""
            response_data = PropertyDetailSerializer(
                property_obj,
                context={'request': request}
            ).data
            
            return self.success_response(
                message="Property updated successfully",
                data=response_data,
                status_code=status.HTTP_200_OK
            )
        
        except Exception as e:
            return self.error_response(
                message="An error occurred while updating the property",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, slug):
        """Delete property"""
        try:
            property_obj = self.get_object(slug)
            
            """Check permission"""
            self.check_object_permissions(request, property_obj)
            
            property_name = property_obj.propertyName
            property_obj.delete()
            
            return self.success_response(
                message=f"Property '{property_name}' deleted successfully",
                data=None,
                status_code=status.HTTP_200_OK
            )
        
        except Exception as e:
            return self.error_response(
                message="An error occurred while deleting the property",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PropertyQRCodeAPIView(CustomResponseMixin, APIView):
    """Generate QR Code for a property with custom JSON response"""

    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        try:
            """Get property object"""
            property_obj = get_object_or_404(Property, slug=slug)
            self.check_object_permissions(request, property_obj)

            """Build property URL"""
            property_url = request.build_absolute_uri(f'/property/{property_obj.slug}/')

            """Prepare QR data"""
            qr_data_text = f"Property Name: {property_obj.propertyName}\n" \
                           f"Address: {property_obj.propertyAddress}\n" \
                           f"URL: {property_url}"

            """Generate QR code"""
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data_text)
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')

            """Save image to memory"""
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            """Encode image as base64 for JSON"""
            img_base64 = base64.b64encode(buffer.read()).decode()

            """Return custom JSON response"""
            return self.success_response(
                message="QR Code generated successfully",
                data={
                    "property_name": property_obj.propertyName,
                    "property_address": property_obj.propertyAddress,
                    "property_url": property_url,
                    "qr_code": img_base64  # can be rendered as image in frontend
                },
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return self.error_response(
                message="An error occurred while generating the QR code",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class FeaturedPropertiesAPIView(CustomResponseMixin, APIView):
    """
    GET: Retrieve top 3 most viewed properties
    Public endpoint - no authentication required
    """
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        """Get top 3 properties by views"""
        try:
            """Get top 3 active properties ordered by total_views"""
            featured_properties = Property.objects.filter(
                status=True
            ).select_related('owner').order_by('-total_views')[:3]
            
            serializer = PropertyListSerializer(
                featured_properties,
                many=True,
                context={'request': request}
            )
            
            return self.success_response(
                message="Featured properties retrieved successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        
        except Exception as e:
            return self.error_response(
                message="An error occurred while retrieving featured properties",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# NEW VIEWS FOR BOOKMARKS

class BookmarkListCreateAPIView(CustomResponseMixin, APIView):
    """
    GET: List all bookmarks for authenticated user
    POST: Create a new bookmark
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all bookmarks for current user"""
        try:
            bookmarks = Bookmark.objects.filter(
                user=request.user
            ).select_related('property', 'property__owner')
            
            serializer = BookmarkSerializer(bookmarks, many=True, context={'request': request})
            
            return self.success_response(
                message="Bookmarks retrieved successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return self.error_response(
                message="An error occurred while retrieving bookmarks",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create a new bookmark"""
        serializer = BookmarkSerializer(data=request.data)
        
        if not serializer.is_valid():
            return self.error_response(
                message="Validation failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            property_obj = Property.objects.get(id=serializer.validated_data['property_id'])
            
            # Check if bookmark already exists
            bookmark, created = Bookmark.objects.get_or_create(
                user=request.user,
                property=property_obj
            )
            
            if not created:
                return self.error_response(
                    message="Property is already bookmarked",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            response_serializer = BookmarkSerializer(bookmark, context={'request': request})
            
            return self.success_response(
                message="Property bookmarked successfully",
                data=response_serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        
        except Property.DoesNotExist:
            return self.error_response(
                message="Property not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.error_response(
                message="An error occurred while creating the bookmark",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BookmarkDetailAPIView(CustomResponseMixin, APIView):
    """
    DELETE: Remove a bookmark
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        """Delete a bookmark"""
        try:
            bookmark = get_object_or_404(
                Bookmark,
                id=pk,
                user=request.user
            )
            
            property_name = bookmark.property.propertyName
            bookmark.delete()
            
            return self.success_response(
                message=f"Bookmark for '{property_name}' removed successfully",
                data=None,
                status_code=status.HTTP_200_OK
            )
        
        except Exception as e:
            return self.error_response(
                message="An error occurred while removing the bookmark",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# NEW VIEWS FOR INSPECTIONS

class InspectionListCreateAPIView(CustomResponseMixin, APIView):
    """
    GET: List all inspections for authenticated user
    POST: Create a new inspection booking
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all inspections for current user"""
        try:
            inspections = Inspection.objects.filter(
                user=request.user
            ).select_related('property', 'property__owner')
            
            serializer = InspectionSerializer(inspections, many=True, context={'request': request})
            
            return self.success_response(
                message="Inspections retrieved successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return self.error_response(
                message="An error occurred while retrieving inspections",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create a new inspection booking"""
        serializer = InspectionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return self.error_response(
                message="Validation failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            property_obj = Property.objects.get(id=serializer.validated_data['property_id'])
            
            inspection = Inspection.objects.create(
                user=request.user,
                property=property_obj,
                inspection_datetime=serializer.validated_data['inspection_datetime']
            )
            
            response_serializer = InspectionSerializer(inspection, context={'request': request})
            
            return self.success_response(
                message="Inspection booked successfully",
                data=response_serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        
        except Property.DoesNotExist:
            return self.error_response(
                message="Property not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.error_response(
                message="An error occurred while booking the inspection",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InspectionDetailAPIView(CustomResponseMixin, APIView):
    """
    GET: Retrieve inspection details
    PATCH: Update inspection datetime
    DELETE: Cancel/delete an inspection
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """Get inspection details"""
        try:
            inspection = get_object_or_404(
                Inspection,
                id=pk,
                user=request.user
            )
            
            serializer = InspectionSerializer(inspection, context={'request': request})
            
            return self.success_response(
                message="Inspection retrieved successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        
        except Exception as e:
            return self.error_response(
                message="An error occurred while retrieving the inspection",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def patch(self, request, pk):
        """Update inspection datetime"""
        try:
            inspection = get_object_or_404(
                Inspection,
                id=pk,
                user=request.user
            )
            
            serializer = InspectionSerializer(
                data=request.data,
                partial=True
            )
            
            if not serializer.is_valid():
                return self.error_response(
                    message="Validation failed",
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            if 'inspection_datetime' in serializer.validated_data:
                inspection.inspection_datetime = serializer.validated_data['inspection_datetime']
                inspection.save()
            
            response_serializer = InspectionSerializer(inspection, context={'request': request})
            
            return self.success_response(
                message="Inspection updated successfully",
                data=response_serializer.data,
                status_code=status.HTTP_200_OK
            )
        
        except Exception as e:
            return self.error_response(
                message="An error occurred while updating the inspection",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, pk):
        """Cancel/delete an inspection"""
        try:
            inspection = get_object_or_404(
                Inspection,
                id=pk,
                user=request.user
            )
            
            property_name = inspection.property.propertyName
            inspection.delete()
            
            return self.success_response(
                message=f"Inspection for '{property_name}' cancelled successfully",
                data=None,
                status_code=status.HTTP_200_OK
            )
        
        except Exception as e:
            return self.error_response(
                message="An error occurred while cancelling the inspection",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# NEW VIEW FOR USER STATISTICS

class UserStatisticsAPIView(CustomResponseMixin, APIView):
    """
    GET: Retrieve user statistics (bookmarks, inspections, total properties)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get comprehensive statistics for current user"""
        try:
            user = request.user
            
            # Get bookmarked properties
            bookmarked_properties = Property.objects.filter(
                bookmarks__user=user
            ).select_related('owner')
            
            # Get upcoming inspections
            upcoming_inspections = Inspection.objects.filter(
                user=user,
                inspection_datetime__gte=timezone.now()
            ).select_related('property', 'property__owner').order_by('inspection_datetime')
            
            # Get total properties in the site
            total_properties = Property.objects.filter(status=True).count()
            
            # Prepare statistics data
            statistics_data = {
                'total_bookmarks': Bookmark.objects.filter(user=user).count(),
                'total_inspections': Inspection.objects.filter(user=user).count(),
                'total_properties': total_properties,
                'bookmarked_properties': bookmarked_properties,
                'upcoming_inspections': upcoming_inspections,
            }
            
            serializer = UserStatisticsSerializer(statistics_data, context={'request': request})
            
            return self.success_response(
                message="User statistics retrieved successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        
        except Exception as e:
            return self.error_response(
                message="An error occurred while retrieving user statistics",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )