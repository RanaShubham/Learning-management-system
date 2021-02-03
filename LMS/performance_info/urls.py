from .views import *
from django.conf import settings
from django.urls.conf import path

app_name = "performance_info"

urlpatterns = [
    path('ratings', GetPerformanceInfo.as_view(), name="get_performance_info_all"),
    path('rating', AddPerformanceInfo.as_view(), name="post_performance_info"),
    path('rating/<int:performance_id>', UpdatePerformanceInfo.as_view(), name="update_delete_performance_info"),
    path('mentor', GetStudentCount.as_view(), name="get-student-count")
]
