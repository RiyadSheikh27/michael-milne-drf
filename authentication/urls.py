from django.urls import path
from .views import *

urlpatterns = [
    path('registration/', registration, name='registration'),
    path('verify-otp/', verify_registration_otp, name='verify_otp'),
    
    path('login/', login, name='login'),
    
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/', reset_password, name='reset_password'),
    path('change-password/', change_password, name='change_password'),
    
    path('profile-data/', get_profile, name='get_profile'),
    path('profile/update/', update_profile, name='update_profile'),
    
    path('users/', user_list, name='user_list'),
    path('users/suspend/<uuid:user_id>/', ChangeUserStatus, name='ChangeUserStatus'),

    path('social-login/', social_login, name='social_login'),
]