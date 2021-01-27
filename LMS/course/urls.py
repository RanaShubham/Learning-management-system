from django.urls import path
from . import views

urlpatterns = [
    path('course/', views.CourseView.as_view(), name="course-register"),
    path('course/<int:pk>/', views.CourseView.as_view(), name="specific-course"),
]
