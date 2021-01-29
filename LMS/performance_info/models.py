from account.models import User
from course.models import Course
from django.db import models
from mentor.models import Mentor


# Create your models here.
class PerformanceInfo(models.Model):
    student_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Student_ID", null=False, blank=False)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="Course_ID", null=False, blank=False)
    score = models.IntegerField(default=00, null=False, blank=False)
    mentor_id = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name = "Mentor_ID",null=False, blank=False)
    assessment_week = models.IntegerField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
