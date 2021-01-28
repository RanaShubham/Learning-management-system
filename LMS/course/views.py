import logging
import os

from django.shortcuts import render

# Create your views here.

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from LMS.utils import LMSException, ExceptionType
from account.utils import Util
from course.models import Course
from course.serializers import CourseSerializer
from services.logging import loggers

logger = loggers("loggers", "log_course.log")


class CourseView(APIView):
    """
    Created a class to perform crud operations for the course which is taken by students
    """
    serializer_class = CourseSerializer

    def post(self, request, **kwargs):
        """

        @param request: name : name of the course
                        @type: str
                        price: price of the course
                        @type: float
                        duration: duration of the course
                        @type: str
                        description: brief explanation about the course
                        @type:str
        @param kwargs[userid]: user of id the authorized user
        @type kwargs: int
        @param kwargs[pk] : primary key of specific course
        @type: int
        """
        try:
            serializer = CourseSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                response = Util.manage_response(status=True, message='course details added', data=serializer.data,
                                                log='course details added', logger_obj=logger)
                return Response(response, status.HTTP_201_CREATED)
            raise LMSException(ExceptionType.UserException, 'Please enter valid details')
        except LMSException as e:
            response = Util.manage_response(status=False, message=e.message,
                                            log=e.message, logger_obj=logger)
            return Response(response, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = Util.manage_response(status=False, message='Something went wrong. Please try again',
                                            log=str(e), logger_obj=logger)
            return Response(response, status.HTTP_400_BAD_REQUEST)

    def get(self, request, **kwargs):
        try:
            if kwargs.get('pk'):
                course = Course.objects.get(id=kwargs.get('pk'))
                if course is None:
                    raise LMSException(ExceptionType.NonExistentError, 'No such course found')
                serializer = CourseSerializer(course)
                response = Util.manage_response(status=True, message='course details retrieved', data=serializer.data,
                                                log='course details retreived', logger_obj=logger)
                return Response(response, status.HTTP_200_OK)
            else:
                courses = Course.objects.all()
                if courses is None:
                    raise LMSException(ExceptionType.NonExistentError, 'No such course found')
                serializer = CourseSerializer(courses)
                response = Util.manage_response(status=True, message='course details retrieved', data=serializer.data,
                                                log='course details retrieved', logger_obj=logger)
                return Response(response, status.HTTP_200_OK)
        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.detail,
                                            log=e.detail, logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False, message='Something went wrong. Please try again',
                                            log=str(e), logger_obj=logger)
            return Response(response, status.HTTP_400_BAD_REQUEST)

    def patch(self, request, **kwargs):
        """

        @param request: name : name of the course
                        @type: str
                        price: price of the course
                        @type: float
                        duration: duration of the course
                        @type: str
                        description: brief explanation about the course
                        @type:str
        @param kwargs[userid]: user of id the authorized user
        @type kwargs: int
        @param kwargs[pk] : primary key of specific course
        @type: int
        """
        try:
            if kwargs.get('pk'):
                course = Course.objects.get(id=kwargs.get('pk'))
                serializer = CourseSerializer(course, data=request.data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    response = Util.manage_response(status=True, message='course details updated', data=serializer.data,
                                                    log='course details updated', logger_obj=logger)
                    return Response(response, status.HTTP_200_OK)
                raise LMSException(ExceptionType.UserException, 'Please enter valid details')
            raise LMSException(ExceptionType.NonExistentError, 'Please enter the specific course id')
        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.detail,
                                            log=e.detail, logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False, message='Something went wrong. Please try again',
                                            log=str(e), logger_obj=logger)
            return Response(response, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        """
        @param kwargs[userid]: user of id the authorized user
        @type kwargs: int
        @param kwargs[pk] : primary key of specific course
        @type: int
        """
        try:
            course = Course.objects.get(id=kwargs['pk'])
            if course is None:
                raise LMSException(ExceptionType.NonExistentError, 'No such course found')
            course.delete()
            response = Util.manage_response(status=True,
                                            message='Deleted successfully.',
                                            log='Deleted course successfully.', logger_obj=logger)
            return Response(response, status.HTTP_204_NO_CONTENT)
        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.detail,
                                            log=e.detail, logger_obj=logger)
            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False, message='Something went wrong. Please try again',
                                            log=str(e), logger_obj=logger)
            return Response(response, status.HTTP_400_BAD_REQUEST)
