from django.urls import path
from django.contrib.auth import views as auth_views

from . import views 

urlpatterns = [
    # User functions
    path('signup', views.registerFunc, name='users-signup'),
    path('login', views.loginFunc, name='users-login'),
    path('logout', views.logoutFunc, name='users-logout'),
    path('activate/(P<uidb64>[0-9A-Za-z_\-]+)/(P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
        views.activate, name='users-activate'),
    
    # Password reset and change
    path('password_reset/', views.forgotPassword,
         name='users-forgot-password'),
    path('password_reset/(P<uidb64>[0-9A-Za-z_\-]+)/(P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
         views.forgotPasswordConfirm, name='users-forgot-password-generator'),
         
    # Profile functions
    path('confirm_user', views.comfirmUser, name='users-confirm-user-type'),
]
