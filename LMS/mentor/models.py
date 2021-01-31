from django.db import models
from account.models import User
from course.models import Course
from django.db.models import Max


class Mentor(models.Model):
    id=models.CharField(primary_key=True,max_length=10,default="MID000")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor')
    course = models.ManyToManyField(Course, related_name='course')
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.name


    def soft_delete(self):
        self.is_deleted = True
        self.save()


    def save(self,**kwargs):
        if self.id=='MID000':
            count = Mentor.objects.count()
            new_id = (str)("{:03d}".format(count+1))
            self.id = "{}{}".format('MID', new_id)
        super().save(**kwargs)