from django.db import models


class Course(models.Model):
    id = models.CharField(primary_key=True, max_length=25, default="CID000")
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

    def save(self, **kwargs):
        if self.id == 'CID000':
            count = Course.objects.count()
            new_id = str("{:03d}".format(count + 1))
            self.id = "{}{}".format('CID', new_id)
        super().save(**kwargs)
