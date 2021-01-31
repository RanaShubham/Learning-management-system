from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    price = models.FloatField(max_length=10, blank=False, null=False)
    duration = models.CharField(max_length=25, blank=False, null=False)
    description = models.CharField(max_length=100, blank=False, null=False)
    is_deleted = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.name

    def soft_delete(self):
        self.is_deleted = True
        self.save()
