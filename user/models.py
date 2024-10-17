from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken
from .manager import UserManager
# Create your models here.
import uuid 
class User(AbstractUser): 
    username=models.CharField(db_index=True, max_length=255, unique=True) 
    email = models.EmailField(max_length=255, db_index=True, unique=True)
    first_name = models.CharField(max_length=30) 
    last_name = models.CharField(max_length=30)
    otp = models.CharField(max_length=6, null=True, blank=True)
    word_limit=models.IntegerField(default=0)
    word_number=models.IntegerField(default=0)
    subscribed = models.BooleanField(default=False)
    # cancel=models.BooleanField(default=False)
    subscriptionid = models.CharField(max_length=70, null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    country=models.CharField(max_length=30, null=True, blank=True)
    current_time = models.DateTimeField(auto_now=True)
    province=models.CharField(max_length=30,null=True, blank=True)
    
    city=models.CharField(max_length=30,null=True, blank=True)
    postalcode=models.CharField(max_length=30,null=True, blank=True)
 
    home=models.CharField(max_length=30,null=True, blank=True)
    dni=models.CharField(max_length=30,null=True, blank=True)
    companyname=models.CharField(max_length=30, null=True, blank=True)

    
    
    objects=UserManager()
    def __str__(self): 
        return self.first_name

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return{
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        }













