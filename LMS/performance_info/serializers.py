from django.db import models
from rest_framework import fields
from rest_framework.serializers import ModelSerializer
from .models import PerformanceInfo, PerformanceFile


class PerformanceInfoSerializer(ModelSerializer):
    class Meta:
        model = PerformanceInfo
        fields = "__all__"

class GetPerformanceInfoSerializer(ModelSerializer):
    class Meta:
        model = PerformanceInfo
        fields = "__all__"
        depth = 2

class PerformanceInfoUpdateSerializer(ModelSerializer):
    class Meta:
        model = PerformanceInfo
        fields = ('assessment_week', 'score')

class PerformanceFileSerializer(ModelSerializer):
    class Meta:
        model = PerformanceFile
        fields = "__all__"
