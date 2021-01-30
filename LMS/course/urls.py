from django.urls import path
from . import views

urlpatterns = [
    path('courses/', views.CoursesView.as_view(), name="courses-details"),
    path('course/', views.CourseRegisterView.as_view(), name="course-register"),
    path('course/<int:pk>/', views.CourseView.as_view(), name="specific-course"),
]
