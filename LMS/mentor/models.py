from django.db import models
from account.models import User
from course.models import Course


class Mentor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor', null=True)
    course = models.ManyToManyField(Course, related_name='courses',blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.name


    def soft_delete(self):
        self.is_deleted = True
        self.save()

