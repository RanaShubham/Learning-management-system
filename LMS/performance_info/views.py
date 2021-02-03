import logging
import os

from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from account.decorators import user_login_required
from account.models import Role, User
from mentor.models import Mentor
from course.models import Course
from services.logging import loggers
from student.models import Student
from account.utils import Util as account_utils
from django.shortcuts import render
from django.utils.decorators import method_decorator
from LMS.utils import ExceptionType, LMSException
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response

from .models import PerformanceInfo
from .serializers import PerformanceInfoSerializer, PerformanceInfoUpdateSerializer, GetStudentCountSerializer

# Create your views here.

logger = loggers("performance_info")


@method_decorator(user_login_required, name='dispatch')
class GetPerformanceInfo(generics.GenericAPIView):
    serializer_class = PerformanceInfoSerializer

    queryset = PerformanceInfo.objects.all()

    def get(self, request, **kwargs):
        """[To get all accessible performance records when logged in as admin or mentor.]

        :param kwargs: [mandatory]:[string]requesting user's id generated from decoded token
        :return:Response with status of success and data if successful.
        """
        try:
            current_user_id = kwargs.get('userid')
            current_user_role = kwargs.get('role')

            if current_user_role != 'admin' and current_user_role != 'mentor':
                raise LMSException(ExceptionType.UnauthorizedError, "You are not authorized to perform this operation." \
                                   , status.HTTP_401_UNAUTHORIZED)

            # If a mentor is accessing this API he should see the performance records
            # of only those students whome he is mentoring.
            if current_user_role == 'mentor':
                current_user_mentor_id = Mentor.objects.get(user=current_user_id).id
                performance_records = PerformanceInfo.objects.filter(mentor_id=current_user_mentor_id, \
                                                                     is_deleted=False)
                logger.info('retrieving list of student performance data for the mentor.')
            else:
                performance_records = PerformanceInfo.objects.filter(is_deleted=False)
                logger.info('retrieving list of student performance data for the admin.')

            serializer = PerformanceInfoSerializer(performance_records, many=True)

            for each in serializer.data:
                student_name = Student.objects.get(id=each.get('student_id'))
                mentor_name = Mentor.objects.get(id=each.get('mentor_id'))
                course_name = Course.objecs.get(id=each.get('course_id'))
                each["student_name"] = student_name
                each['mentor_name'] = mentor_name
                each['course_name'] = course_name

            response = account_utils.manage_response(status=True, message='Retrieved performance records.',
                                                     data=serializer.data,
                                                     log='retrieved perfromance records', logger_obj=logger)
            return Response(response, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            response = account_utils.manage_response(status=False, message=e.detail, log=e.detail, logger_obj=logger)
        except Mentor.DoesNotExist as e:
            response = account_utils.manage_response(status=False, message="Mentor not found.", log=str(e),
                                                     logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist as e:
            response = account_utils.manage_response(status=False, message="Course not found.", log=str(e),
                                                     logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Student.DoesNotExist as e:
            response = account_utils.manage_response(status=False, message="Student not found.", log=str(e),
                                                     logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Role.DoesNotExist as e:
            response = account_utils.manage_response(status=False,
                                                     message="Please make sure that admin and mentor both roles are present.",
                                                     log=str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except LMSException as e:
            response = account_utils.manage_response(status=False, message=e.message, log=e.message, logger_obj=logger)
            return Response(response, e.status_code, content_type="application/json")
        except Exception as e:
            response = account_utils.manage_response(status=False, message="Something went wrong.Please try again",
                                                     log=str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(user_login_required, name='dispatch')
class AddPerformanceInfo(generics.GenericAPIView):
    serializer_class = PerformanceInfoSerializer

    def get_queryset(self):
        pass

    def post(self, request, **kwargs):
        """[To add performance record for a student when logged in as admin or mentor.]

        :param kwargs: [mandatory]:[string]requesting user's id generated from decoded token.
        :param request: [mandatory]:[charfield]:[student_id] student's student_id whose record is to be added. 
                      : [manadatory]:[charfield]:[course_id] course's course_id that student will take.
                      : [manadatory]:[charfield]:[mentor_id] mentor's mentor_id
                      : [mandatory]:[Integer]:[Assesment_week] Assesment week for the student. Default will be set to 1.
                      : [optional]:[Float]:[Score] Score value of student performance. Default will be set to 00.00
        :return:Response with status of success and data if successful.
        """
        try:
            current_user_role = kwargs.get('role')

            course_id = request.data.get("course_id")
            student_id = request.data.get("student_id")

            # To make sure that a student is mapped to a course only once.
            if PerformanceInfo.objects.filter(course_id=course_id, student_id=student_id):
                raise LMSException(ExceptionType.PerformanceRecordExists, \
                                   "A performance record of this student for this course already exists.")

            # If current user is neither mentor or an admin he can't add a performance record.
            if current_user_role != 'admin' and current_user_role != 'mentor':
                raise LMSException(ExceptionType.UnauthorizedError, \
                                   "You are not authorized to perform this operation.", status.HTTP_401_UNAUTHORIZED)

            # If current user is admin then he can simply add a valid performance record for anyone.
            if current_user_role == 'admin':
                serializer = PerformanceInfoSerializer(request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                response = account_utils.manage_response(status=True, message='Added performance record.', \
                                                         log='Added perfromance record', logger_obj=logger)
                return Response(response, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            response = account_utils.manage_response(status=False, message=e.detail, log=e.detail, logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = account_utils.manage_response(status=False, message="Something went wrong.", \
                                                     log=str(e), logger=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(user_login_required, name='dispatch')
class UpdatePerformanceInfo(generics.GenericAPIView):
    serializer_class = PerformanceInfoUpdateSerializer

    def get_queryset(self):
        pass

    def patch(self, request, **kwargs):
        """[To update performance record for a student when logged in as mentor.]

        :param kwargs: [mandatory]:[string] requesting user's id generated from decoded token.
                        [manadatory]:[String] course id of the course that is to be updated.
        :param request: [optional]:[Integer]:[Assesment_week] Assesment week for the student. Default will be set to 1.
                      : [optional]:[Float]:[Score] Score value of student performance. Default will be set to 00.00
        :return:Response with status of success and data if successful.
        """
        try:
            current_user_role = kwargs.get('role')
            record_id_to_be_updated = kwargs.get("performance_id")

            # If current user is not mentor he can't update a performance record.
            if current_user_role != 'mentor':
                raise LMSException(ExceptionType.UnauthorizedError, \
                                   "You are not authorized to perform this operation.", status.HTTP_401_UNAUTHORIZED)

            record_to_be_updated = PerformanceInfo.objects.get(id=record_id_to_be_updated, is_deleted=False)
            serializer = PerformanceInfoUpdateSerializer(record_to_be_updated, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = account_utils.manage_response(status=True, message='Updated performance record.', \
                                                     log='Updated perfromance record', logger_obj=logger)
            return Response(response, status=status.HTTP_200_OK)
        except PerformanceInfo.DoesNotExist as e:
            response = account_utils.manage_response(status=False, message="Performance record does not exist.", \
                                                     log=str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except serializers.ValidationError as e:
            response = account_utils.manage_response(status=False, message=e.detail, log=e.detail, logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = account_utils.manage_response(status=False, message="Something went wrong.", \
                                                     log=str(e), logger=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        """[To delete performance record for a student when logged in as admin.]

        :param kwargs: [mandatory]:[string] requesting user's id generated from decoded token.
                        [manadatory]:[String] course id of the course that is to be delete.
        :return:Response with status of success and data if successful.
        """
        try:
            current_user_role = kwargs.get('role')
            record_id_to_be_updated = kwargs.get("performance_id")

            # If current user is not admin he can't delete a performance record.
            if current_user_role != 'admin':
                raise LMSException(ExceptionType.UnauthorizedError, \
                                   "You are not authorized to perform this operation.", status.HTTP_401_UNAUTHORIZED)

            record_to_be_deleted = PerformanceInfo.objects.get(id=record_id_to_be_updated, is_deleted=False)
            record_to_be_deleted.is_deleted = True
            record_to_be_deleted.save()
            response = account_utils.manage_response(status=True, message='Deleted performance record.', \
                                                     log='Deleted perfromance record', logger_obj=logger)
            return Response(response, status=status.HTTP_200_OK)
        except PerformanceInfo.DoesNotExist as e:
            response = account_utils.manage_response(status=False, message="Performance record does not exist.", \
                                                     log=str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = account_utils.manage_response(status=False, message="Something went wrong.", \
                                                     log=str(e), logger=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @method_decorator(user_login_required, name='dispatch')
class GetStudentCount(generics.GenericAPIView):
    """
    Created a class to get all students with mentor id and course id
    """
    serializer_class = GetStudentCountSerializer

    mentor_param_config = openapi.Parameter(
        'mentor_id', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)
    course_param_config = openapi.Parameter(
        'course_id', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[mentor_param_config, course_param_config])
    def get(self, request, **kwargs):
        """
        [To get number of students taken the respective course and mentor when logged in as admin.]
        :param kwargs: [mandatory]:[string]requesting user's id generated from decoded token
        :return:Response with status of success and data if successful.

        "parameters": [
        {
            "name": "performance/mentor",
            "in": "query",
            "description": "The performance info that needs to be fetched.",
            "type": "string"
        }
    ]
        """
        try:
            # if kwargs['role'] == 'admin':
            performance = PerformanceInfo.objects.filter(mentor_id=request.GET.get('mentor_id')).filter(
                course_id=request.GET.get('course_id'))
            if performance is None:
                raise LMSException(ExceptionType.NonExistentError, "No performance record matching the criteria",
                                   status.HTTP_404_NOT_FOUND)

            count = performance.count()
            performance_obj = PerformanceInfo.objects.filter(mentor_id=request.GET.get('mentor_id')).filter(
                course_id=request.GET.get('course_id')).first()
            course_name = performance_obj.course_id.name
            student_list = []
            for item in performance:
                student = Student.objects.filter(id=item.student_id).first()
                info = {'name': student.user.name, 'score': item.score}
                student_list.append(info)
            stud_dict = {'count': count, 'course_name': course_name, 'student_info': student_list}
            response = account_utils.manage_response(status=True, message='Retrieved details of students.',
                                                     log='Retrieved details of students', data=stud_dict,
                                                     logger_obj=logger)
            return Response(response, status=status.HTTP_200_OK)
        except LMSException as e:
            response = account_utils.manage_response(status=False, message=e.message, log=e.message, logger_obj=logger)
            return Response(response, e.status_code, content_type="application/json")
        except Exception as e:
            response = account_utils.manage_response(status=False, message="Something went wrong.Please try again",
                                                     log=str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
