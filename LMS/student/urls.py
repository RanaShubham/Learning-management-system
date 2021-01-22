from django.urls import path
from . import views

urlpatterns = [
    path('student/', views.StudentDetails.as_view(), name="student-register"),
    path('student/<int:pk>/', views.StudentDetails.as_view(), name="student-details"),
]
