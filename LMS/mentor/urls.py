from django.urls import re_path, path
from .views import *

urlpatterns = [
    re_path(r'^(?P<pk>[0-9]{0,})$', AdminView.as_view(), name="admin_get"),
    path('profile/',MentorProfile.as_view(),name="get"),
]
