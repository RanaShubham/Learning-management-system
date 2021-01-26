from django.db import models
from account.models import User


class Mentor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor', null=True)
    course = models.CharField(max_length=50, blank=False, null=False)
    #TODO:course = models.ForeignKey(Course,on_delete=models.CASCADE, related_name='course', null=True)

    def __str__(self):
        return self.user.name
