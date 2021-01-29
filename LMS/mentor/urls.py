from django.urls import re_path, path
from .views import *

urlpatterns = [
    path('users', AdminView.as_view(), name="get_mentors"),
    path('user', MentorProfile.as_view(), name="post_mentor"),
    path('user/<int:pk>', MentorProfile.as_view(), name="delete_mentor"),
]
