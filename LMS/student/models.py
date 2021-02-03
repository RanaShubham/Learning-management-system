from django.db import models
from account.models import User


class Student(models.Model):
    id = models.CharField(primary_key=True, max_length=10, default="SID000")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author', null=True)  # name of user
    alternate_contact_number = models.CharField(max_length=13, blank=True, default=None, null=True)
    relationship_of_alternate_contact_person = models.CharField(max_length=20, blank=True, default=None, null=True)
    current_location = models.CharField(max_length=20, blank=True, default=None, null=True)
    current_address = models.TextField(blank=True, default=None, null=True)
    git_link = models.TextField(blank=True, default=None, null=True)
    college_name = models.CharField(max_length=50, blank=True, default=None, null=True)
    university = models.CharField(max_length=50, blank=True, default=None, null=True)
    degree = models.CharField(max_length=20, blank=True, default=None, null=True)
    degree_stream = models.CharField(max_length=20, blank=True, default=None, null=True)
    degree_percentage = models.FloatField(max_length=5, blank=True, default=None, null=True)
    degree_graduation_year = models.IntegerField(blank=True, default=None, null=True)
    masters = models.CharField(max_length=20, blank=True, default=None, null=True)
    masters_stream = models.CharField(max_length=20, blank=True, default=None, null=True)
    masters_percentage = models.FloatField(max_length=5, blank=True, default=None, null=True)
    year_of_job_experience = models.IntegerField(blank=True, default=None, null=True)
    year_of_masters = models.IntegerField(blank=True, default=None, null=True)

    def __str__(self):
        return self.user.email

    def save(self, **kwargs):
        if self.id == 'SID000':
            count = Student.objects.count()
            new_id = str("{:03d}".format(count + 1))
            self.id = "{}{}".format('SID', new_id)
        super().save(**kwargs)



