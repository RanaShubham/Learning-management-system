import pytest
from rest_framework import status

from LMS.utils import LMSException
from performance_info.models import PerformanceInfo
from mixer.backend.django import mixer


@pytest.mark.django_db
class TestAccount:
    def test_model_performance_info(self):
        student_obj = mixer.blend('performance_info.PerformanceInfo')
        assert student_obj.pk == 1, 'Should save an instance'

    def test_user_performance_info_is_soft_deleted(self):
        user_obj = mixer.blend('performance_info.PerformanceInfo',is_deleted = False)
        user_obj.soft_delete()
        assert user_obj.is_deleted == True