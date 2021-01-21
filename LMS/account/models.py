from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from LMS.utils import ExceptionType, LMSException
from .utils import Util, get_random_password

class UserManager(BaseUserManager):
    
    def create_user(self, email, password='password', is_active=True, name=None, role=None, phone_number=None):
        '''
            Method to create a user record for the database.
            Throws vlaue error if no email is provided.
            Throws value error if no password is provided.
        '''
        if not name:
            raise LMSException(ExceptionType, "User must have a name.")
        if not role:
            raise LMSException(ExceptionType, "User must have a role.")
        if not email:
            raise LMSException(ExceptionType.UserException, "User must have an email.")
        if not password:
            raise LMSException(ExceptionType.UserException, "User must have a password.")
        if not phone_number:
            raise LMSException(ExceptionType.UserException, "User must have a phone number")

        user_obj = self.model(
            email = self.normalize_email(email),
        )
        
        user_obj.password = password
        user_obj.name = name
        user_obj.role = role
        user_obj.phone_number= phone_number
        user_obj.set_password(password)
        user_obj.is_active = is_active
        user_obj.save(using=self.db)
        return user_obj


class User(AbstractBaseUser):
    email = models.EmailField(max_length=128, unique=True)
    name = models.CharField(max_length=32, blank=False, null=False)
    phone_number = models.CharField(max_length=10, blank=False, null=False)
    role = models.CharField(max_length=16, null=False, blank=False)
    is_deleted = models.BooleanField(default=False)
    is_active= models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        '''
            To display an object in the Django admin site and as the value inserted
            into a template when it displays an object.
        '''
        return self.email
