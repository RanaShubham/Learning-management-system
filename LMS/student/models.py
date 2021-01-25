from django.db import models
from account.models import User


class Student(models.Model):
    student_id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author', null=True)  # name of user
    email = models.CharField(max_length=30)
    alternate_contact_number = models.CharField(max_length=13, blank=False, null=False)
    relationship_of_alternate_contact_person = models.CharField(max_length=20, blank=False, null=False)
    current_location = models.CharField(max_length=20, blank=False, null=False)
    current_address = models.TextField(blank=False, null=False)
    git_link = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.email


class Education(models.Model):
    student_id = models.IntegerField(blank=False, null=False)
    course = models.CharField(max_length=50, blank=False, null=False)
    institution = models.CharField(max_length=50, blank=False, null=False)
    date_of_joined = models.IntegerField(blank=False, null=False)
    date_of_graduated = models.IntegerField(blank=False, null=False)
    Percentage = models.FloatField(max_length=5, blank=False, null=False)

    def __int__(self):
        return self.student_id
