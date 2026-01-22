from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from .models import *
from .serializers import *
from utils.permissions import IsAdmin, IsAdminOrReadOnly, IsOwnerOrReadOnly

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
    permission_classes = [IsOwnerOrReadOnly]

    def get(self, request):
        """List all active properties"""
        try:
            properties = Property.objects.all().select_related('owner')
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

    # @transaction.atomic
    # def post(self, request):
    #     """Create a new property"""
    #     serializers = PropertyCreateUpdateSerializer(data=request.data)



