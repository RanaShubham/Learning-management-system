from rest_framework import serializers

from course.models import Course


class CourseSerializer(serializers.ModelSerializer):
    """
    created a serializer class to serialize and deserialize the data
    """

    class Meta:
        model = Course
        fields = '__all__'
