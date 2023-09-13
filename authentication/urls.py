
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from .views import *
  
urlpatterns = [
    path('',UserRegister.as_view(),name='User Register'),
    path('register/',UserRegister.as_view(),name='User Register'),
    path('login/',UserLogin.as_view(),name='User Login'),
    path('user/profile/',UserProfile.as_view(),name="User Profile")
]