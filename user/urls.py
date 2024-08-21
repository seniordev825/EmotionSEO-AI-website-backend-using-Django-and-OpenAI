from . import views
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('validat/', views.ValidateOTP.as_view(), name='validate'),
    path('register/',views.RegisterView.as_view(),name="register"),
    path('login/',views.LoginAPIView.as_view(),name="login"),
    
    path('logout/', views.LogoutAPIView.as_view(), name="logout"),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('service/', views.FreeServiceUsageView.as_view(), name="service"),
    path('subscribea/', views.Producta.as_view(), name='subscribea'),
    path('subscribeb/', views.Productb.as_view(), name='subscribeb'),
    path('subscribec/', views.Productc.as_view(), name='subscribec'),
    path('invoice/', views.FreeServiceUsageView2.as_view(), name='subscribe2'),
    path('generateimage/', views.generateimage, name='image'), 
    path('generateimagepost/', views.generateimage1, name='imagepost'),
    path('image/', views.image, name='image1'), 
    path('generating/', views.generating, name='generate'),
    path('getinfo/', views.GetInfo.as_view(), name='getinfo'),
    path('password_reset/', views.forgotnew, name='password_reset'),
    path('reset_password/confirm/<uidb64>/<token>/', views.reset_password_confirm, name='reset_password_confirm'),
    path('confirm_password/', views.confirm_password, name='confirm_password'),
    path('cancelsubscription/', views.CancelSubscription.as_view(), name='cancelsubscription'),
    path('post/', views.PostView.as_view(), name='postview'),
    path('image/', views.image, name='imagegeneration'),
    path('imagepost/', views.image1, name='imagegeneration'),
  
    path("auth/google/", views.GoogleLoginApi.as_view(), 
         name="login-with-googlea"),
    path('delete/', views.DeleteAccount.as_view(),name='deleteaccount')
   
]