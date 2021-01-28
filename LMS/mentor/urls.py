from django.urls import re_path, path
from .views import *

urlpatterns = [
    path('all',AdminView.as_view(), name='admin-get'),
    path('get/<int:pk>',MentorProfile.as_view(),name="get-mentor"),
    path('post',MentorProfile.as_view(),name="post"),
    path('delete/<int:pk>',MentorProfile.as_view(),name="delete-mentor"),
]
