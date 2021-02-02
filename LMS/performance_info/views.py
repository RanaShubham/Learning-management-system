import logging
import os

from account.decorators import user_login_required
from account.models import Role, User
from mentor.models import Mentor
from course.models import Course
from student.models import Student
from account.utils import Util as account_utils
from django.shortcuts import render
from django.utils.decorators import method_decorator
from LMS.utils import ExceptionType, LMSException
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response

from .models import PerformanceInfo
from .serializers import PerformanceInfoSerializer

#TODO: Mentor can add score, week and rest performance info of student.
#TODO: Mentor can update score or week or anything.
#Mentor can get all details for all student.
#TODO: M<entor can get all details of one student.
#TODO: Mentor can delete performance info of a student.
# Create your views here.

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')

file_handler = logging.FileHandler(os.path.abspath("loggers/log_accounts.log"))
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


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
                raise LMSException(ExceptionType.UnauthorizedError,"You are not authorized to perform this operation."\
                    ,status.HTTP_401_UNAUTHORIZED)

            #If a mentor is accessing this API he should see the performance records
            #of only those students whome he is mentoring.
            if current_user_role == 'mentor':
                current_user_mentor_id = Mentor.objects.get(user = current_user_id).id
                performance_records = PerformanceInfo.objects.filter(mentor_id = current_user_mentor_id,\
                     is_deleted = False)
                logger.info('retrieving list of student performance data for the mentor.')
            else:
                performance_records = PerformanceInfo.objects.filter(is_deleted=False)
                logger.info('retrieving list of student performance data for the admin.')

            serializer = PerformanceInfoSerializer(performance_records, many=True)

            x = serializer.data
            #TODO:MODIFY SERIALIZED DATA TO CONTAIN STUDENT NAME, COURSE NAME, AND MENTOR NAME.
            response = account_utils.manage_response(status=True, message='Retrieved performance records.',data=serializer.data,
                                            log='retrieved perfromance records', logger_obj=logger)
            return Response(response, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            response = account_utils.manage_response(status=False, message=e.detail, log=e.detail, logger_obj=logger)
        except Mentor.DoesNotExist as e:
            response = account_utils.manage_response(status=False, message = "You are not a mentor.", log=str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Role.DoesNotExist as e:
            response = account_utils.manage_response(status=False, message = "Please make sure that admin and mentor both roles are present.",
                                                    log = str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except LMSException as e:
            response = account_utils.manage_response(status=False, message=e.message, log=e.message, logger_obj=logger)
            return Response(response, e.status_code, content_type="application/json")
        except Exception as e:
            response = account_utils.manage_response(status=False, message="Something went wrong.Please try again", log=str(e), logger_obj=logger)
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

            #To make sure that a student is mapped to a course only once.
            if PerformanceInfo.objects.filter(course_id=course_id, student_id=student_id):
                raise LMSException(ExceptionType.PerformanceRecordExists, \
                    "A performance record of this student for this course already exists.")

            #If current user is neither mentor or an admin he can't add a performance record.
            if current_user_role != 'admin' and current_user_role != 'mentor':
                raise LMSException(ExceptionType.UnauthorizedError,\
                    "You are not authorized to perform this operation.",status.HTTP_401_UNAUTHORIZED)

            #If current user is admin then he can simply add a valid performance record for anyone.
            if current_user_role == 'admin':
                serializer = PerformanceInfoSerializer(request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                response = account_utils.manage_response(status=True, message='Added performance record.',\
                    log='Added perfromance record', logger_obj=logger)
                return Response(response, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            response = account_utils.manage_response(status=False, message=e.detail, log=e.detail, logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = account_utils.manage_response(status=False, message = "Something went wrong.", \
                log = str(e), logger = status.HTTP_500_INTERNAL_SERVER_ERROR)