"""
Test Models
"""
import pytest
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db


class TestCourse:
    def test_init(self):
        course_obj = mixer.blend('course.Course', name='java')
        assert course_obj.name == 'java', 'Should save an instance'