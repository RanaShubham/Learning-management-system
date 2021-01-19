from django.contrib import admin
from .models import User as user
# from django.contrib.auth import get_user_model

# Register your models here.
User = user

admin.site.register(User)