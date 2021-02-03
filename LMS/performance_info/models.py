# from account.models import User
from student.models import Student
from course.models import Course
from django.db import models
from mentor.models import Mentor


# Create your models here.
class PerformanceInfo(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="Student_ID", null=False, blank=False)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="Course_ID", null=False, blank=False)
    score = models.FloatField(default=00.00, null=False, blank=False)
    mentor_id = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name = "Mentor_ID",null=False, blank=False)
    assessment_week = models.IntegerField(default=1, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)


    def soft_delete(self):
        self.is_deleted = True
        self.save()