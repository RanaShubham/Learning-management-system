from django.db import models
from rest_framework import fields, serializers
from rest_framework.serializers import ModelSerializer
from .models import PerformanceInfo


class PerformanceInfoSerializer(ModelSerializer):
    class Meta:
        model = PerformanceInfo
        fields = "__all__"


class PerformanceInfoUpdateSerializer(ModelSerializer):
    class Meta:
        model = PerformanceInfo
        fields = ('assessment_week', 'score')


class GetStudentCountSerializer(serializers.ModelSerializer):

    class Meta:
        model = PerformanceInfo
        fields = ['mentor_id', 'course_id']
