from django.db import models


class Student(models.Model):
    name = models.CharField(max_length=50, default=None, blank=False, null=False)
    phone_number = models.CharField(max_length=13, default=None, blank=False, null=False)
    alternate_contact_number = models.CharField(max_length=13, default=None, blank=False, null=False)
    relationship_of_alternate_contact_person = models.CharField(max_length=20, default=None, blank=False, null=False)
    current_location = models.CharField(max_length=20, default=None, blank=False, null=False)
    current_address = models.TextField(blank=False, null=False)
    git_link = models.TextField(blank=False, null=False)
    college_name = models.CharField(max_length=50, default=None, blank=False, null=False)
    university = models.CharField(max_length=50, default=None, blank=False, null=False)
    degree = models.CharField(max_length=20, default=None, blank=False, null=False)
    degree_stream = models.CharField(max_length=20, default=None, blank=False, null=False)
    degree_percentage = models.FloatField(max_length=5, default=None, blank=False, null=False)
    degree_graduation_year = models.IntegerField(max_length=5, default=None, blank=False, null=False)
    masters = models.CharField(max_length=20, default=None, blank=True, null=True)
    masters_stream = models.CharField(max_length=20, default=None, blank=True, null=True)
    masters_percentage = models.FloatField(max_length=5, default=None, blank=True, null=True)
    year_of_job_experience = models.IntegerField(max_length=50, default=None, blank=True, null=True)
    year_of_masters = models.IntegerField(max_length=5, default=None, blank=True, null=True)

    def __str__(self):
        return self.name
