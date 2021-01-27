import pytest
from mixer.backend.django import mixer


@pytest.mark.django_db
class TestAccount:
    def test_model(self):
        student_obj = mixer.blend('account.User')
        assert student_obj.pk == 1, 'Should save an instance'

@pytest.mark.django_db
class TestRole:
    def test_model(self):
        student_obj = mixer.blend('account.Role')
        assert student_obj.pk == 1, 'Should save an instance'