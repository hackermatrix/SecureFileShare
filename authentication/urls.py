
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from .views import *
  
urlpatterns = [
    path('user/register/',UserRegister.as_view(),name='User Register'),
    path('user/login/',UserLogin.as_view(),name='User Login')
]