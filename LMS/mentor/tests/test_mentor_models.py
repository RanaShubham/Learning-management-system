import pytest
from mixer.backend.django import mixer


@pytest.mark.django_db
class TestMentor:
    def test_model(self):
        mentor_obj = mixer.blend('mentor.Mentor')
        assert mentor_obj.pk == 'MID001', 'Should save a mentor instance'


    def test_mentor_is_soft_deleted(self):
        mentor_obj = mixer.blend('mentor.Mentor',is_deleted = False)
        mentor_obj.soft_delete()
        assert mentor_obj.is_deleted == True

    def test__str__(self):
        user_obj = mixer.blend('account.User', name='admin',email='admin@gmail.com')
        mentor_obj = mixer.blend('mentor.Mentor', user=user_obj)
        assert str(mentor_obj) == 'admin'
