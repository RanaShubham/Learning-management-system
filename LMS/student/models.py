from django.db import models
from account.models import User


class Student(models.Model):
    id = models.CharField(primary_key=True, max_length=10, default="SID000")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author', null=True)
    is_deleted = models.BooleanField(default=False)
    image = models.ImageField(upload_to='avatar/', default=None, null=True)
    alternate_contact_number = models.CharField(max_length=13, default=None, blank=True, null=True)
    relationship_of_alternate_contact_person = models.CharField(max_length=20, default=None, blank=True, null=True)
    current_location = models.CharField(max_length=20, default=None, blank=True, null=True)
    current_address = models.TextField(default=None, blank=True, null=True)
    git_link = models.TextField(default=None, blank=True, null=True)
    college_name = models.CharField(max_length=50, default=None, blank=True, null=True)
    university = models.CharField(max_length=50, default=None, blank=True, null=True)
    degree = models.CharField(max_length=20, default=None, blank=True, null=True)
    degree_stream = models.CharField(max_length=20, default=None, blank=True, null=True)
    degree_percentage = models.FloatField(max_length=5, default=None, blank=True, null=True)
    degree_start_year = models.IntegerField(blank=True, default=None, null=True)
    degree_graduation_year = models.IntegerField(blank=True, default=None, null=True)
    masters = models.CharField(max_length=20, blank=True, null=True)
    masters_stream = models.CharField(max_length=20, blank=True, null=True)
    masters_percentage = models.FloatField(max_length=5, blank=True, null=True)
    masters_degree_start_year = models.IntegerField(blank=True, default=None, null=True)
    masters_degree_graduation_year = models.IntegerField(blank=True, default=None, null=True)
    year_of_job_experience = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.id

    def save(self, **kwargs):
        if self.id == 'SID000':
            count = Student.objects.count()
            new_id = str("{:03d}".format(count + 1))
            self.id = "{}{}".format('SID', new_id)
        super().save(**kwargs)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

class StudentCreate(models.Model):
    email = models.EmailField(max_length=128, unique=True)
    name = models.CharField(max_length=32, blank=False, null=False)
    phone_number = models.CharField(max_length=10, blank=False, null=False)
    course_id = models.CharField(max_length=32, blank=False, null=False)
    mentor_id = models.CharField(max_length=32, blank=False, null=False)
