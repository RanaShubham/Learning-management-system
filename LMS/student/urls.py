from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('student/', views.CreateStudent.as_view(), name="student-register"),
    path('students/', views.StudentsDetails.as_view(), name="student-retrieve"),
    path('student/<int:pk>/', views.StudentDetails.as_view(), name="specific-course"),
    path('students-upload/', views.AddStudentByFile.as_view(), name = "add-student-by-file")

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
