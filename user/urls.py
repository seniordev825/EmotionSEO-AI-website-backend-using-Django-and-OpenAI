from . import views
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('validate/', views.ValidateOTP.as_view(), name='validate'),
    path('register/',views.RegisterView.as_view(),name="register"),
    path('login/',views.LoginAPIView.as_view(),name="login"),   
    path('logout/', views.LogoutAPIView.as_view(), name="logout"),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('service/', views.FreeServiceUsageView.as_view(), name="service"),
    path('subscribe-a/', views.ProductA.as_view(), name='subscribe_a'),
    path('subscribe-b/', views.ProductB.as_view(), name='subscribe_b'),
    path('subscribe-c/', views.ProductC.as_view(), name='subscribe_c'),
    path('invoice/', views.Invoice.as_view(), name='subscribe2'),
    path('generate-image-article/', views.generateImageCaseArticle, name='image'), 
    path('generate-image-post/', views.generateImageCasePost, name='imagepost'),
    path('generating/', views.generatingSEOKeywords, name='generate'),
    path('getinfo/', views.GetInfo.as_view(), name='getinfo'),
    path('password_reset/', views.forgotNew, name='password_reset'),
    path('reset_password/confirm/<uidb64>/<token>/', views.reset_password_confirm, name='reset_password_confirm'),
    path('confirm_password/', views.confirm_password, name='confirm_password'),
    path('cancelsubscription/', views.CancelSubscription.as_view(), name='cancelsubscription'),
    path('post/', views.PostView.as_view(), name='postview'),
    path('display-stability-image/', views.display_stability_image, name='display_stability_image'),
    path('display-openai-image/', views.display_openai_image, name='display_openai_image'),
    path("auth/google/", views.GoogleLoginApi.as_view(), 
         name="login-with-googlea"),
    path('delete/', views.DeleteAccount.as_view(),name='deleteaccount')
   
]
