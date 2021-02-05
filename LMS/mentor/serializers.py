from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Mentor,MentorPost

User = get_user_model()


class MentorSerializer(serializers.ModelSerializer):
    """
    this class is used for serialization and deserialization of mentor details
    """

    class Meta:
        model = Mentor
        fields = ['course','user', 'id','image']

class MentorPostSerializer(serializers.ModelSerializer):
    """
    this class is used for serialization and deserialization of mentor details
    """

    class Meta:
        model = MentorPost
        fields = ['email','name', 'phone_number','role','course']





