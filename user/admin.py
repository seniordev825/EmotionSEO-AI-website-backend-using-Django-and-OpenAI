from django.contrib import admin
from user.models import User


class YourModelAdmin(admin.ModelAdmin):
    list_display = ('username','first_name','id','email', 'current_time', 'otp', 'city', 'postalcode', 'home', 'dni','companyname', "word_limit", "word_number","subscribed", "subscriptionid","usage_count")

admin.site.register(User, YourModelAdmin)
