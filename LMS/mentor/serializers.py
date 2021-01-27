from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Mentor
from account.serializers import RegisterSerializer

User = get_user_model()


class MentorSerializer(serializers.ModelSerializer):
    """
    this class is used for serialization and deserialization of mentor details
    """
    #user = RegisterSerializer(read_only=True)

    class Meta:
        model = Mentor
        fields = ['course','user']
        depth = 2


