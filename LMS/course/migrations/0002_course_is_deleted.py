# Generated by Django 3.1.3 on 2021-01-31 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='is_deleted',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
