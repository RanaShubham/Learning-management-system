import pytest
from rest_framework import status

from LMS.utils import LMSException
from account.models import User
from mixer.backend.django import mixer


@pytest.mark.django_db
class TestAccount:
    def test_model(self):
        student_obj = mixer.blend('account.User')
        assert student_obj.pk == 1, 'Should save an instance'

    def test_user_is_soft_deleted(self):
        user_obj = mixer.blend('account.User',is_deleted = False)
        user_obj.soft_delete()
        assert user_obj.is_deleted == True

    def test_superuser_with_is_staff_False(self):
        with pytest.raises(LMSException):
            User.objects.create_superuser(name="admin", email="admin@email.com", phone_number="1234567890",
                                          password="adminpass",is_staff=False)

    def test_superuser_with_is_superuser_False(self):
        with pytest.raises(LMSException):
            User.objects.create_superuser(name="admin", email="admin@email.com", phone_number="1234567890",
                                          password="adminpass",is_superuser=False)

    def test_create_user_with_no_name(self):
        with pytest.raises(LMSException):
            User.objects.create_user( name="",email="admin@email.com", phone_number="1234567890",
                                        role="mentor")

    def test_create_user_with_no_role(self):
        with pytest.raises(LMSException):
            User.objects.create_user( name="mentorX",email="admin@email.com", phone_number="1234567890",
                                        role="")
    def test_create_user_with_no_email(self):
        with pytest.raises(LMSException):
            User.objects.create_user( name="mentorX",email="", phone_number="1234567890",
                                        role="mentor")

    def test_create_user_with_no_phone_number(self):
        with pytest.raises(LMSException):
            User.objects.create_user( name="admin",email="admin@email.com", phone_number="",
                                        role="admin")
    def test__str__(self):
        user_obj = mixer.blend('account.User', name='admin',email='admin@gmail.com')
        assert str(user_obj) == 'admin@gmail.com'


@pytest.mark.django_db
class TestRole:
    def test_model(self):
        student_obj = mixer.blend('account.Role')
        assert student_obj.pk == 1, 'Should save an instance'