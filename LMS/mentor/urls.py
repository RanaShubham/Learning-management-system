from django.urls import re_path, path
from .views import *

app_name = "mentor"


urlpatterns = [
    path('users', AdminView.as_view(), name="get_mentors"),
    path('user', CreateMentor.as_view(), name="post_mentor"),
    path('user/<int:pk>', MentorProfile.as_view(), name="get_update_delete_mentor"),
]
