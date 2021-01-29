from rest_framework.serializers import ModelSerializer
from .models import PerformanceInfo

class PerformanceInfoSerializer(ModelSerializer):
    class Meta:
        model = PerformanceInfo
        fields = "__all__"