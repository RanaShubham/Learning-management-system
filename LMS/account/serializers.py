from django.contrib import auth
from .models import User
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

class RegisterSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['id','email', 'name', 'role','phone_number',]


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
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)

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


