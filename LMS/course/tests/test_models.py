"""
Test Models
"""
import pytest
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db


class TestCourse:
    def test_init(self):
        course_obj = mixer.blend('course.Course', pk=1)
        assert course_obj.pk == 1, 'Should save an instance'