from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Student

User = get_user_model()


class StudentSerializer(serializers.ModelSerializer):
    """
    this class is used for serialization and deserialization of student details
    """

    class Meta:
        model = Student
        fields = '__all__'
