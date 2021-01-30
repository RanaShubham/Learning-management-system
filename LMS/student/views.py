import logging
import os

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, generics

from services.logging import loggers
from .serializers import StudentSerializer
from .models import Student
from django.utils.decorators import method_decorator
from account.decorators import user_login_required
from account.models import User
from django.db.models import Q
from LMS.utils import *
from account.utils import Util

logger = loggers("loggers", "log_students.log")


@method_decorator(user_login_required, name='dispatch')
class StudentsDetails(generics.GenericAPIView):
    serializer_class = StudentSerializer
    queryset = Student.objects.all()

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
        try:
            if kwargs['role'] == 'student':
                user = User.objects.get(id=kwargs['userid'])
                details = Student.objects.filter(Q(email=user.email)).first()
                if details is None:
                    request.POST._mutable = True
                    request.data["user"] = kwargs['userid']
                    request.data['email'] = user.email
                    request.data['student_id'] = kwargs['userid']
                    request.POST._mutable = False
                    serializer = StudentSerializer(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        response = Util.manage_response(status=True, message='student details added',
                                                        data=serializer.data,
                                                        log='student details added', logger_obj=logger)
                        return Response(response, status.HTTP_201_CREATED)
                    raise LMSException(ExceptionType.UserException, 'Please enter valid details',
                                       status.HTTP_400_BAD_REQUEST)
                else:
                    raise LMSException(ExceptionType.StudentExist, 'student already exist', status.HTTP_400_BAD_REQUEST)
            raise LMSException(ExceptionType.UserException, 'you are not a student to create profile',
                               status.HTTP_401_UNAUTHORIZED)
        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=str(e), logger_obj=logger)

            return Response(response, e.status_code, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False,
                                            message="some other issue occurred",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")

    def get(self, request, **kwargs):
        """
        [displays specific student data ]
        args: kwargs[pk]: user id of the user
        Returns:
            Response: status , message and data
            @type: status: Boolean, message:str, data: list
        """
        try:
            if kwargs['role'] == 'admin':
                student_list = Student.objects.all()
                serializer = StudentSerializer(student_list, many=True)
                response = Util.manage_response(status=True, message='student details retrieved',
                                                data=serializer.data,
                                                log='student details retrieved', logger_obj=logger)
                return Response(response, status.HTTP_200_OK)
            else:
                raise LMSException(ExceptionType.UserException,
                                   "Sorry,you are not authorized to perform this operation.",
                                   status.HTTP_401_UNAUTHORIZED)
        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=str(e), logger_obj=logger)

            return Response(response, e.status_code, content_type="application/json")
        except User.DoesNotExist:
            response = Util.manage_response(status=False,
                                            message='The student does not exist',
                                            log='The student does not exist', logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False,
                                            message="some other issue occurred",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")


@method_decorator(user_login_required, name='dispatch')
class StudentDetails(generics.GenericAPIView):
    serializer_class = StudentSerializer
    queryset = Student.objects.all()

    def get(self, request, **kwargs):
        """
        [displays specific student data ]
        args: kwargs[pk]: user id of the user
        Returns:
            Response: status , message and data
            @type: status: Boolean, message:str, data: list
        """
        try:
            user = User.objects.get(id=kwargs['userid'])  # requesting user:admin/student
            student = User.objects.get(id=kwargs['pk'])  # student's personal details
            student_details = Student.objects.filter(Q(email=student.email)).first()
            if student_details is None:
                raise LMSException(ExceptionType.StudentNotFound, 'No such student found', status.HTTP_400_BAD_REQUEST)
            elif student_details.email == user.email or kwargs['role'] == 'admin':
                serializer = StudentSerializer(student_details)
                data = serializer.data
                data['phone_number'] = user.phone_number
                response = Util.manage_response(status=True, message='student details retrieved',
                                                data=data,
                                                log='student details retrieved', logger_obj=logger)
                return Response(response, status.HTTP_200_OK)
            else:
                raise LMSException(ExceptionType.UserException,
                                   "Sorry,you are not authorized to perform this operation.",
                                   status.HTTP_401_UNAUTHORIZED)
        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=str(e), logger_obj=logger)

            return Response(response, e.status_code, content_type="application/json")
        except User.DoesNotExist:
            response = Util.manage_response(status=False,
                                            message='The student does not exist',
                                            log='The student does not exist', logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False,
                                            message="some other issue occurred",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")

    def patch(self, request, *args, **kwargs):
        """
        [updates the respective student data ]
        args: kwargs[pk]: user id of the user
        Returns:
            Response: status , message and data
            @type: status: Boolean, message:str, data: list
        """
        try:
            user = User.objects.get(id=kwargs['userid'])
            details = Student.objects.filter(Q(email=user.email)).first()
            if details is None:
                raise LMSException(ExceptionType.UserException,
                                   "Sorry,you are not authorized to perform this operation.",
                                   status.HTTP_401_UNAUTHORIZED)
            if details.user_id == kwargs['pk']:
                data = request.data
                serializer = StudentSerializer(details, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    response = Util.manage_response(status=True, message='data updated successfully',
                                                    data=serializer.data,
                                                    log='data updated successfully', logger_obj=logger)
                    return Response(response, status.HTTP_200_OK)
                response = Util.manage_response(status=False,
                                                message='please enter the valid details',
                                                log='please enter the valid details', logger_obj=logger)
                return Response(response, status.HTTP_400_BAD_REQUEST)
            else:
                raise LMSException(ExceptionType.UserException,
                                   "Sorry,you are not authorized to perform this operation.",
                                   status.HTTP_401_UNAUTHORIZED)
        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=str(e), logger_obj=logger)

            return Response(response, e.status_code, content_type="application/json")
        except Student.DoesNotExist:
            response = Util.manage_response(status=False,
                                            message='The student does not exist',
                                            log='The student does not exist', logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False,
                                            message="some other issue occurred",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")
