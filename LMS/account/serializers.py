from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from .models import User
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from LMS.utils import *


class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'phone_number', ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(ModelSerializer):
    """[validates user credentials and allows login if authenticated]

    Raises:
        AuthenticationFailed: [if improper credentials are passed]
        AuthenticationFailed: [if user account is not active]

    Returns:
        [string]: [email]
    """
    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(
        max_length=68, min_length=3, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, attrs):
        """
        it verifies the credentials, if credentials were matched then returns data in json format, else throws exception
        :return: return json data if credentials are matched
        """
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        user = auth.authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed('Invalid credentials, please try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')

        return {
            'email': user.email,
        }

class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    """
    this serializer class is used for serialization and deserialization of data while requesting for reset password
    """
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']

class SetNewPasswordSerializer(serializers.Serializer):
    """
    this serializer class is used for serialization and deserialization of data while setting new password
    """
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        """
        it take new password and confirm password and if the password matches all criteria then it will set new password
        :rtype: data of the user and its success status
        """
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise LMSException(ExceptionType.UnAuthorized, "The reset link is invalid")

            user.set_password(password)
            user.save()

            return user
        except Exception as e:
            raise LMSException(ExceptionType.UnauthorizedError, "The reset link is invalid")