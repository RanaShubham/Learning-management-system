from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import StudentSerializer
from .models import Student


class StudentDetails(APIView):
    serializer_class = StudentSerializer
    data = {"status": False, "message": 'some other issue'}

    def post(self, request):
        """
        A method to post student details
        @param request: name: name of student (mandatory)
                        @type:str
                        phone_number: phone number of student (mandatory)
                        @type:str
                        college: college the student admitted
                        @type:str
                        git_link: git link of the student
                        @type:str

        @return: status, message and status code
        @rtype: status: boolean, message: str
        """
        try:
            serializer = StudentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                self.data["status"] = True
                self.data["message"] = 'student details added'
                self.data['data'] = serializer.data
                return Response(self.data, status.HTTP_201_CREATED)
            self.data['message'] = 'Please enter valid details'
            return Response(self.data, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            self.data['exception'] = str(e)
            return Response(self.data, status.HTTP_400_BAD_REQUEST)

    def get(self, request, **kwargs):
        """
        [displays specific student data ]
        args: kwargs[pk]: user id of the user
        Returns:
            Response: status , message and data
            @type: status: Boolean, message:str, data: list
        """
        try:
            student = Student.objects.get(id=kwargs.get('pk'))  # retrieving data from database
            serializer = StudentSerializer(student)
            self.data['status'] = True
            self.data['message'] = 'student details added'
            self.data['data'] = serializer.data
            return Response(self.data, status.HTTP_200_OK)
        except Student.DoesNotExist as e:
            self.data["message"] = 'Student does not exist'
            return Response(self.data, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            self.data["exception"] = str(e)
            return Response(self.data, status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        """
        [updates the respective student data ]
        args: kwargs[pk]: user id of the user
        Returns:
            Response: status , message and data
            @type: status: Boolean, message:str, data: list
        """
        try:
            item = Student.objects.get(pk=kwargs.get('pk'))
            data = request.data
            serializer = StudentSerializer(item, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                self.data['status'] = True
                self.data['message'] = 'data updated successfully'
                self.data['data'] = serializer.data
                return Response(self.data, status.HTTP_200_OK)
            self.data['message']: "please enter the valid details"
            return Response(self.data, status.HTTP_400_BAD_REQUEST)
        except Student.DoesNotExist:
            self.data["exception"] = "Student does not exist"
            return Response(self.data, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            self.data["exception"] = str(e)
            return Response(self.data, status.HTTP_400_BAD_REQUEST)
