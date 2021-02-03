from django.urls import path
from . import views

urlpatterns = [

    path('student/', views.CreateStudent.as_view(), name="student-register"),
    path('students/', views.StudentsDetails.as_view(), name="student-retrieve"),
    path('student/<int:pk>/', views.StudentDetails.as_view(), name="specific-course"),

]
