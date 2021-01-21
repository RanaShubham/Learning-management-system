"""
Test Models
"""
import pytest
from mixer.backend.django import mixer


@pytest.mark.django_db
class TestStudent:
    def test_model(self):
        student_obj = mixer.blend('student.Student')
        assert student_obj.pk == 1, 'Should save an instance'
