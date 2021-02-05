from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import serializers

from performance_info.models import PerformanceInfo
from .models import Student, StudentCreate
from account.models import User

User = get_user_model()


class StudentSerializer(serializers.ModelSerializer):
    """
    this class is used for serialization and deserialization of student details
    """

    class Meta:
        model = Student
        fields = '__all__'


class RegisterStudentSerializer(serializers.ModelSerializer):
    """
    this class is used for serialization and deserialization of student details
    """

    class Meta:
        model = StudentCreate
        fields = ['email', 'name', "phone_number", "course_id", "mentor_id"]
