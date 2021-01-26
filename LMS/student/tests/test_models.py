"""
Test Models
"""
import pytest
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db


class TestStudent:
    def test_init(self):
        student_obj = mixer.blend('student.Student', pk=1)
        assert student_obj.pk == 1, 'Should save an instance'
