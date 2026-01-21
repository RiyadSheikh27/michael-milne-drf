from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from .models import Users
from .serializers import *
from utils.tokens import get_tokens_for_user
from utils.permissions import IsAdmin
import random
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

@api_view(['POST'])
@permission_classes([AllowAny])
def registration(request):
    """Step 1: Register user and send OTP"""
    serializer = RegistrationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    otp = str(random.randint(1000, 9999))
    
    try:
        subject = 'Email Verification - OTP'
        message = f'Your OTP for registration is: {otp}\n\nThis OTP is valid for 5 minutes.'
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        cache.set(f'registration_{email}', {
            'otp': otp,
            'data': serializer.validated_data
        }, timeout=300)
        print(otp)
        
        return Response({
            'success': True,
            'message': f'OTP sent to {email}',
            'email': email
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to send OTP. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_registration_otp(request):
    """Step 2: Verify OTP for both registration and password reset"""
    serializer = VerifyOTPSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    otp = serializer.validated_data['otp']
    
    """Check for registration OTP"""
    registration_data = cache.get(f'registration_{email}')
    if registration_data and registration_data['otp'] == otp:
        try:
            user_data = registration_data['data']
            password = user_data.pop('password')
            
            user = Users.objects.create(**user_data)
            user.set_password(password)
            user.is_active = True
            user.save()
            
            cache.delete(f'registration_{email}')
            tokens = get_tokens_for_user(user)
            
            return Response({
                'success': True,
                'message': 'Registration completed successfully',
                'user': UserProfileSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to create user. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    password_reset_otp = cache.get(f'password_reset_{email}')
    if password_reset_otp and password_reset_otp == otp:
        cache.set(f'verified_{email}', True, timeout=60)
        
        return Response({
            'success': True,
            'message': 'OTP verified successfully. Please set your new password.',
            'email': email
        }, status=status.HTTP_200_OK)
    
    """If no match found"""
    return Response({
        'success': False,
        'message': 'Invalid or expired OTP.'
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login user"""
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = serializer.validated_data['user']
    tokens = get_tokens_for_user(user)
    
    return Response({
        'success': True,
        'message': 'Login successful',
        'user': UserProfileSerializer(user).data,
        'tokens': tokens
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """Send OTP for password reset"""
    serializer = ForgotPasswordSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    otp = str(random.randint(1000, 9999))
    
    try:
        subject = 'Password Reset - OTP'
        message = f'Your OTP for password reset is: {otp}\n\nThis OTP is valid for 5 minutes.'
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        cache.set(f'password_reset_{email}', otp, timeout=300)
        
        return Response({
            'success': True,
            'message': f'OTP sent to {email}',
            'email': email
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to send OTP. Please try again.{e}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password after OTP verification"""
    serializer = ResetPasswordSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    new_password = serializer.validated_data['new_password']
    
    """ Check if OTP was verified"""
    is_verified = cache.get(f'verified_{email}')
    if not is_verified:
        return Response({
            'success': False,
            'message': 'Please verify OTP first.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = Users.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        
        """ Clean up cache"""
        cache.delete(f'password_reset_{email}')
        cache.delete(f'verified_{email}')
        
        return Response({
            'success': True,
            'message': 'Password reset successfully'
        }, status=status.HTTP_200_OK)
        
    except Users.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found.'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change password for authenticated user"""
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    new_password = serializer.validated_data['new_password']
    
    user.set_password(new_password)
    user.save()
    
    return Response({
        'success': True,
        'message': 'Password changed successfully'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """Get user profile"""
    serializer = UserProfileSerializer(request.user)
    return Response({
        'success': True,
        'user': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile"""
    serializer = UpdateProfileSerializer(
        request.user, 
        data=request.data, 
        partial=True
    )
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer.save()
    
    return Response({
        'success': True,
        'message': 'Profile updated successfully',
        'user': UserProfileSerializer(request.user).data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdmin])
def user_list(request):
    """Get all users (Admin only)"""
    users = Users.objects.all().order_by('-created_at')

    total_users = users.count()
    total_active_users = users.filter(is_active=True).count()
    total_inactive_users = users.filter(is_active=False).count()

    serializer = UserListSerializer(users, many=True)
    
    return Response({
        'success': True,
        'messgae': "Users retrieved successfully",
        'statistics': {
            'total_users': total_users,
            'total_active_users': total_active_users,
            'total_inactive_users': total_inactive_users
        },
        'users': serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAdmin])
def ChangeUserStatus(request, user_id):
    user = get_object_or_404(Users, id=user_id)
    serializer = UserStatusChangeSerializer(user, data=request.data)

    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer.save()
    return Response({
        'success': True,
        'message': 'User suspended successfully',
        'user': UserStatusChangeSerializer(user).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def social_login(request):
    email = request.data.get('email')
    full_name = request.data.get('full_name')
    auth_provider = request.data.get('auth_provider')
    image_url = request.data.get('image')

    """Validate required fields"""
    if not email or not full_name or not auth_provider:
        return Response({
            "status": "error",
            "message": "Missing required fields",
            "errors": {
                "email": "This field is required." if not email else None,
                "full_name": "This field is required." if not full_name else None,
                "auth_provider": "This field is required." if not auth_provider else None,
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    """Get or create user"""
    user, created = Users.objects.get_or_create(
        email=email,
        defaults={
            'username': email,
            'full_name': full_name,
            'auth_provider': auth_provider,
        }
    )

    """If user already exists, update fields if needed"""
    if not created:
        user.full_name = full_name
        user.auth_provider = auth_provider
        user.save()

    """Handle image URL - download and save if provided"""
    if image_url and (created or not user.image):
        try:
            import requests
            from django.core.files.base import ContentFile
            from urllib.parse import urlparse
            import os

            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                """Extract filename from URL or generate one"""
                parsed_url = urlparse(image_url)
                filename = os.path.basename(parsed_url.path) or f"{user.id}_profile.jpg"
                
                user.image.save(
                    filename,
                    ContentFile(response.content),
                    save=True
                )
        except Exception as e:
            print(f"Error downloading image: {e}")
            """Continue without image - don't fail the signup"""

    """Generate tokens"""
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token

    token = {
        'refresh': str(refresh),
        'access': str(access_token),
    }

    user_details = {
        'id': user.id,
        'full_name': user.full_name,
        'email': user.email,
        'image': user.image.url if user.image else None,
    }

    return Response({
        'status': 'success',
        'message': 'Successfully authenticated.',
        'user': user_details,
        'token': token,
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    