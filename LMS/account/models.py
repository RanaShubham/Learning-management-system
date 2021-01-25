from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from LMS.utils import ExceptionType, LMSException


class UserManager(BaseUserManager):

    def create_superuser(self, name, email, phone_number, password, role, **other_fields):
        """
        takes details of the user as input and if all details are valid then it will create superuser profile
        """
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise LMSException(ExceptionType.UserException,
                               'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise LMSException(ExceptionType.UserException,
                               'Superuser must be assigned to is_superuser=True.')

        return self.create_user(name=name, email=email, role=role,
                                password=password, phone_number=phone_number, **other_fields)

    def create_user(self, email, name, role, phone_number, password='password', **other_fields):
        """
        takes details of the user as input and if all credentials are valid then it will create user
        """
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

        email = self.normalize_email(email)
        user = self.model(name=name, email=email, role=role, phone_number=phone_number,
                          password=password, **other_fields)

        user.name = name
        user.role = role
        user.phone_number = phone_number
        user.is_active = True
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=128, unique=True)
    name = models.CharField(max_length=32, blank=False, null=False)
    phone_number = models.CharField(max_length=10, blank=False, null=False)
    role = models.CharField(max_length=16, null=False, blank=False)
    is_deleted = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'role', 'phone_number']

    def __str__(self):
        '''
            To display an object in the Django admin site and as the value inserted
            into a template when it displays an object.
        '''
        return self.email

    def soft_delete(self):
        self.is_deleted = True
        self.save()
