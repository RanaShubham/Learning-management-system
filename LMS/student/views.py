from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import StudentSerializer
from .models import Student
from django.utils.decorators import method_decorator
from account.decorators import user_login_required
from account.models import User
from django.db.models import Q
from LMS.utils import *


@method_decorator(user_login_required, name='dispatch')
class StudentDetails(APIView):
    serializer_class = StudentSerializer
    data = {"status": False, "message": 'some other issue'}

    def post(self, request, **kwargs):
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
        data = {"status": False, "message": 'some other issue'}
        try:

            user = User.objects.get(id=kwargs['userid'])
            details = Student.objects.filter(Q(email=user.email)).first()
            if details is None:
                request.POST._mutable = True
                request.data["user"] = kwargs['userid']
                request.data['email'] = user.email
                request.POST._mutable = False
                serializer = StudentSerializer(data=request.data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    data["status"] = True
                    data["message"] = 'student details added'
                    data['data'] = serializer.data
                    return Response(data, status.HTTP_201_CREATED)
                raise LMSException(ExceptionType.UserException, 'Please enter valid details')
            else:
                raise LMSException(ExceptionType.StudentExist, 'student already exist')
        except LMSException as e:
            data['message'] = e.message
            return Response(data, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data['exception'] = str(e)
            return Response(data, status.HTTP_400_BAD_REQUEST)

    def get(self, request, **kwargs):
        """
        [displays specific student data ]
        args: kwargs[pk]: user id of the user
        Returns:
            Response: status , message and data
            @type: status: Boolean, message:str, data: list
        """
        data = {"status": False, "message": 'some other issue'}
        try:
            if kwargs.get('pk'):

                user = User.objects.get(id=kwargs['userid'])  # requesting user:admin/student
                student = User.objects.get(id=kwargs['pk'])  # student's personal details

                student_details = Student.objects.filter(Q(email=student.email)).first()
                if student_details is None:
                    raise LMSException(ExceptionType.StudentNotFound, 'No such student found')

                elif student_details.email == user.email or user.role == 'admin':
                    serializer = StudentSerializer(student_details)
                    data['status'] = True
                    data['message'] = 'student details retrieved'
                    data['data'] = serializer.data
                    return Response(data, status.HTTP_200_OK)
                else:
                    raise LMSException(ExceptionType.UserException,
                                       "Sorry,you are not authorized to perform this operation.")
            else:
                user = User.objects.get(id=kwargs['userid'])
                if user.role == 'admin':
                    student_list = Student.objects.all()

                    serializer = StudentSerializer(student_list, many=True)
                    data['status'] = True
                    data['message'] = 'student details retrieved'
                    data['data'] = serializer.data
                    return Response(data, status.HTTP_200_OK)
                else:
                    raise LMSException(ExceptionType.UserException,
                                       "Sorry,you are not authorized to perform this operation.")
        except LMSException as e:
            data["message"] = e.message
            return Response(data, status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            data["message"] = 'Student does not exist'
            return Response(data, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data["exception"] = str(e)
            return Response(data, status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        """
        [updates the respective student data ]
        args: kwargs[pk]: user id of the user
        Returns:
            Response: status , message and data
            @type: status: Boolean, message:str, data: list
        """
        data = {"status": False, "message": 'some other issue'}
        try:
            user = User.objects.get(id=kwargs['userid'])

            details = Student.objects.filter(Q(email=user.email)).first()
            if details.user_id == kwargs['pk']:
                data = request.data
                serializer = StudentSerializer(details, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    data['status'] = True
                    data['message'] = 'data updated successfully'
                    data['data'] = serializer.data

                    return Response(data, status.HTTP_200_OK)
                data['message']: "please enter the valid details"
                return Response(data, status.HTTP_400_BAD_REQUEST)
            else:
                raise LMSException(ExceptionType.UserException,
                                   "Sorry,you are not authorized to perform this operation.")
        except LMSException as e:
            data["message"] = e.message
            return Response(data, status.HTTP_400_BAD_REQUEST)
        except Student.DoesNotExist:
            data["exception"] = "Student does not exist"
            return Response(data, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data["exception"] = str(e)
            return Response(data, status.HTTP_400_BAD_REQUEST)
