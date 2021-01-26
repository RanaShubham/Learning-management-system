from django.db import models
from account.models import User


class Course(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    price = models.FloatField(max_length=10, blank=False, null=False)
    duration = models.CharField(max_length=25, blank=False, null=False)
    description = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return self.name
