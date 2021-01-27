from django.db import models
from account.models import User
from course.models import Course


class Mentor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor')
    course = models.ForeignKey(Course,on_delete=models.CASCADE, related_name='course')
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.name


    def soft_delete(self):
        self.is_deleted = True
        self.save()

