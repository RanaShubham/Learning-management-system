from django.urls import path
from . import views

urlpatterns = [
    path('students/', views.StudentsDetails.as_view(), name="students-details"),
    path('student/', views.StudentsDetailsRegister.as_view(), name="student-register"),
    path('student/<int:pk>/', views.StudentDetails.as_view(), name="student-details"),
]
