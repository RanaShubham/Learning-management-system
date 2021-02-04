from LMS.utils import admin_only
import logging
import os

from django.db.models import Q

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
from .serializers import GetPerformanceInfoSerializer, PerformanceInfoSerializer, PerformanceInfoUpdateSerializer

# Create your views here.

logger = loggers("performance_info")


@method_decorator(user_login_required, name='dispatch')
class GetPerformanceInfo(generics.GenericAPIView):
    serializer_class = PerformanceInfoSerializer

    queryset = PerformanceInfo.objects.select_related("student_id", "mentor_id", "course_id")
    
    def get(self, request, **kwargs):
        """[To get all accessible performance records when logged in as admin or mentor.]

        :param kwargs: [mandatory]:[string]requesting user's id generated from decoded token
        :return:Response with status of success and data if successful.
        """
        try:
            current_user_id = kwargs.get('userid')
            current_user_role = kwargs.get('role')

            logger.info('User with id {id} and role {role} making get request to get performance records.'.\
                format(id=current_user_id, role=current_user_role))

            if current_user_role != 'admin' and current_user_role != 'mentor':
                raise LMSException(ExceptionType.UnauthorizedError, "You are not authorized to perform this operation." \
                                   , status.HTTP_401_UNAUTHORIZED)

            # If a mentor is accessing this API he should see the performance records
            # of only those students whome he is mentoring.
            if current_user_role == 'mentor':
                current_user_mentor_id = Mentor.objects.get(user = current_user_id).id
                performance_records = PerformanceInfo.objects\
                    .filter(mentor_id = current_user_mentor_id, is_deleted = False)\
                        # .select_related("student_id", "mentor_id", "course_id")
                logger.info('retrieving list of student performance data for the mentor.')
            else:
                performance_records = PerformanceInfo.objects.filter(is_deleted=False)
                    # .select_related("student_id", "mentor_id", "course_id").values()
                logger.info('retrieving list of student performance data for the admin.')

            serializer = GetPerformanceInfoSerializer(performance_records, many=True)
            for each in serializer.data:
                each['student_name'] = each.get('student_id').get('user').get('name')
                each['mentor_name'] = each.get('mentor_id').get('user').get('name')
                each['course_name'] = each.get('course_id').get('name')

                each['student_id'] = each.get('student_id').get('id')
                each['mentor_id'] = each.get('mentor_id').get('id')
                each['course_id'] = each.get('course_id').get('id')

            response = account_utils.manage_response(status=True, message='Retrieved performance records.',
                                                     data=serializer.data,
                                                     log='retrieved perfromance records', logger_obj=logger)
            return Response(response, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            response = account_utils.manage_response(status=False, message=e.detail, log=e.detail, logger_obj=logger)
        except Role.DoesNotExist as e:
            response = account_utils.manage_response(status=False,
                                                     message="Please make sure that admin and mentor both roles are present.",
                                                     log=str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except LMSException as e:
            response = account_utils.manage_response(status=False, message=e.message, log=e.message, logger_obj=logger)
            return Response(response, e.status_code, content_type="application/json")
        except Exception as e:
            response = account_utils.manage_response(status=False, message=str(e),
                                                     log=str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(user_login_required, name='dispatch')
class AddPerformanceInfo(generics.GenericAPIView):
    serializer_class = PerformanceInfoSerializer

    queryset = PerformanceInfo.objects.all()

    @admin_only
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
            course_id = request.data.get("course_id")
            student_id = request.data.get("student_id")

            logger.info('Performance record with course with id {id} and student id {student} has been requested to add.'.\
                format(id=course_id, student=student_id))

            # To make sure that a student is mapped to a course only once.
            if PerformanceInfo.objects.filter(course_id=course_id, student_id=student_id):
                logger.warning("Failed to add performance record because similar performance record for the student\
                     already exists.")
                raise LMSException(ExceptionType.PerformanceRecordExists, \
                                   "A performance record of this student for this course already exists.",\
                                       status.HTTP_400_BAD_REQUEST)

            serializer = PerformanceInfoSerializer(data = request.data)
            serializer.is_valid(raise_exception=True)
            logger.info('Added performance record.')
            serializer.save()
            response = account_utils.manage_response(status=True, message='Added performance record.', \
                                                        log='Added perfromance record', logger_obj=logger)
            return Response(response, status=status.HTTP_200_OK)
        except LMSException as e:
            response = account_utils.manage_response(status=False, message=str(e), log=str(e), logger_obj=logger)
            return Response(response, status=e.status_code)
        except serializers.ValidationError as e:
            response = account_utils.manage_response(status=False, message=e.detail, log=e.detail, logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = account_utils.manage_response(status=False, message=str(e), \
                                                     log=str(e), logger=status.HTTP_500_INTERNAL_SERVER_ERROR)



@method_decorator(user_login_required, name='dispatch')
class UpdatePerformanceInfo(generics.GenericAPIView):
    serializer_class = PerformanceInfoUpdateSerializer

    queryset = PerformanceInfo.objects.all()

    def patch(self, request, **kwargs):
        """[To update performance record for a student when logged in as mentor.]

        :param kwargs: [mandatory]:[string] requesting user's id generated from decoded token.
        :param request: [optional]:[Integer]:[Assesment_week] Assesment week for the student. Default will be set to 1.
                      : [optional]:[Float]:[Score] Score value of student performance. Default will be set to 00.00
                      : [manadatory]: [str]: [student id] student id of the student whose record is to be updated.
                      : [manadatory]: [str]: [course id] course id of the course whose evaluation score is to be updated.
        :return:Response with status of success and data if successful.
        """
        try:
            current_user_role = kwargs.get('role')
            current_user_id = kwargs.get('userid')
            #If current user is not mentor or admin he can't update a performance record.
            if current_user_role != 'mentor' and current_user_role != 'admin':
                raise LMSException(ExceptionType.UnauthorizedError,\
                    "You are not authorized to perform this operation.",status.HTTP_401_UNAUTHORIZED)

            student_id = request.get('student_id')
            course_id = request.get('course_id')

            if current_user_role == 'mentor':
                mentor_id = Mentor.objects.get(user = current_user_id).id
                record_to_be_updated = PerformanceInfo.objects.get(course_id = course_id, \
                                                    student_id = student_id, mentor_id = mentor_id, is_deleted=False)
                if record_to_be_updated and request.data.get('score'):
                    record_to_be_updated.update(score = request.data.get('score'))
                else:
                    raise LMSException(ExceptionType.NoPerformanceRecord,\
                        "No performance record was found.", status.HTTP_400_BAD_REQUEST)

                if record_to_be_updated and request.data.get('assessment_week'):
                    record_to_be_updated.update(assessment_week = request.data.get('assessment_week'))

                logger.info('Updated performance record by a mentor.')
                response = account_utils.manage_response(status=True, message='Updated performance record.', \
                                                        log='Updated perfrormance record.', logger_obj=logger)
                return Response(response, status=status.HTTP_200_OK)
            else:
                record_to_be_updated = PerformanceInfo.objects.get(course_id = course_id, \
                                                    student_id = student_id, is_deleted=False)

                if not record_to_be_updated:
                    raise LMSException(ExceptionType.NoPerformanceRecord,\
                        "No performance record was found.", status.HTTP_400_BAD_REQUEST)

                serializer = PerformanceInfoSerializer(record_to_be_updated, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                logger.info('Updated performance record by admin.')
                serializer.save()
                response = account_utils.manage_response(status=True, message='Updated performance record.', \
                                                        log='Updated performance record.', logger_obj=logger)
                return Response(response, status=status.HTTP_200_OK)
        except LMSException as e:
            response = account_utils.manage_response(status=False, message="Performance record does not exist.", \
                                                     log=str(e), logger_obj=logger)
        except PerformanceInfo.DoesNotExist as e:
            response = account_utils.manage_response(status=False, message="Performance record does not exist.", \
                                                     log=str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except serializers.ValidationError as e:
            response = account_utils.manage_response(status=False, message=e.detail, log=e.detail, logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = account_utils.manage_response(status=False, message = "Something went wrong.", \
                log = str(e), logger = status.HTTP_500_INTERNAL_SERVER_ERROR)

    @admin_only
    def delete(self, request, **kwargs):
        """[To delete performance record for a student when logged in as admin.]

        :param kwargs: [mandatory]:[string] requesting user's id generated from decoded token.
                        [manadatory]:[String] course id of the course that is to be delete.
        :return:Response with status of success and data if successful.
        """
        try:
            current_user_role = kwargs.get('role')
            record_id_to_be_updated = kwargs.get("performance_id")

            record_to_be_deleted = PerformanceInfo.objects.get(id=record_id_to_be_updated, is_deleted = False)
            record_to_be_deleted.is_deleted = True
            record_to_be_deleted.save()
            logger.info('Deleted performance record.')
            response = account_utils.manage_response(status=True, message='Deleted performance record.', \
                                                     log='Deleted perfromance record', logger_obj=logger)
            return Response(response, status=status.HTTP_200_OK)
        except LMSException as e:
            response = account_utils.manage_response(status=False, message=str(e),\
                 log=str(e), logger_obj=logger)
            return Response(response, status=e.status_code)
        except PerformanceInfo.DoesNotExist as e:
            response = account_utils.manage_response(status=False, message="Performance record does not exist.", \
                                                     log=str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = account_utils.manage_response(status=False, message = "Something went wrong.", \
                log = str(e), logger = status.HTTP_500_INTERNAL_SERVER_ERROR)
            response = account_utils.manage_response(status=False, message="Something went wrong.", \
                                                     log=str(e), logger=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(user_login_required, name='dispatch')
class GetStudentCount(generics.GenericAPIView):
    """
    Created a class to get all students with mentor id and course id
    """
    def get(self, request, **kwargs):
        """[To get number of students taken the respective course and mentor when logged in as admin.]

        :param kwargs: [mandatory]:[string]requesting user's id generated from decoded token
        :return:Response with status of success and data if successful.
        """
        try:
            if kwargs['role'] == 'admin':
                performance = PerformanceInfo.objects.filter(mentor_id=request.GET.get('mentor_id')).filter(course_id=request.GET.get('course_id'))
                if performance is None:
                    raise LMSException(ExceptionType.NonExistentError, "No performance record matching the criteria", status.HTTP_404_NOT_FOUND)
                student_list = []
                for item in performance:
                    student = Student.objects.filter(id=item.student_id).first()
                    info = {"name": student.user.name, 'score': item.score}
                    student_list.append(info)
                response = account_utils.manage_response(status=True, message='Retrieved details of students.',
                                                         log='Retrieved details of students', data=student_list,
                                                         logger_obj=logger)
                return Response(response, status=status.HTTP_200_OK)
        except LMSException as e:
            response = account_utils.manage_response(status=False, message=e.message, log=e.message, logger_obj=logger)
            return Response(response, e.status_code, content_type="application/json")
        except Exception as e:
            response = account_utils.manage_response(status=False, message="Something went wrong.Please try again",
                                                     log=str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
