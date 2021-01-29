from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Student
from account.models import User

User = get_user_model()


class StudentSerializer(serializers.ModelSerializer):
    """
    this class is used for serialization and deserialization of student details
    """
    student_id = serializers.IntegerField(required=False)

    class Meta:
        model = Student
        fields = '__all__'
