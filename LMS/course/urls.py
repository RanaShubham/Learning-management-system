from django.urls import path
from . import views

urlpatterns = [
    path('course/', views.CourseRegisterView.as_view(), name="course-register"),
    path('course/<int:pk>/', views.CourseView.as_view(), name="specific-course"),
    path('courses/', views.retrieve_courses, name = "courses-retrieve"),
    path('specific-course/<int:pk>/', views.retrieve_course, name = "course-retrieve"),
]
