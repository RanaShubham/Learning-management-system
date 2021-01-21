from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import User

class RegisterSerializer(ModelSerializer):
    # password = serializers.CharField(
    #     max_length=68, min_length=6, write_only=True)

    # default_error_messages = {
    #     'username': 'The username should only contain alphanumeric characters'}

    class Meta:
        model = User
        fields = ['email', 'name', 'role','phone_number', ]#'password'

    # def validate(self, attrs):
    #     email = attrs.get('email', '')
    #     user_name = attrs.get('user_name', '')

    #     if not user_name.isalnum():
    #         raise serializers.ValidationError(
    #             self.default_error_messages)
    #     return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)