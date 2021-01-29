import logging
import os

from account.decorators import user_login_required
from account.models import Role, User
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
    def get_queryset(self):
        pass
    def get(self, request, **kwargs):
        """[To get all the registered User details when logged in as admin.]

        :param kwargs: [mandatory]:[string]dictionary containing requesting user's id generated from decoded token
        :return:Response with status of success and data if successful.
        """
        try:
            current_user_id = kwargs.get('userid')
            admin_role_id = Role.objects.get(role='admin').role_id
            current_user_role_id = User.objects.get(id=current_user_id).role.role_id
            mentor_role_id = Role.objects.get(role='mentor').role_id
            
            if current_user_role_id != admin_role_id or current_user_role_id != mentor_role_id:
                raise LMSException(ExceptionType.UnauthorizedError,"You are not authorized to perform this operation.",status.HTTP_401_UNAUTHORIZED)

            #If a mentor is accessing this API he should see the performance of only those students which he is mentoring.
            if current_user_role_id == mentor_role_id:
                performance_records = PerformanceInfo.objects.filter(mentor_id = mentor_role_id)
                logger.info('retrieving list of student performance data for the mentor.')
            else:
                performance_records = PerformanceInfo.objects.all()
                logger.info('retrieving list of student performance data for the admin.')

            serializer = PerformanceInfoSerializer(performance_records, many=True)
            response = account_utils.manage_response(status=True, message='Retrieved performance records.',data=serializer.data,
                                            log='retrieved perfromance records', logger_obj=logger)
            return Response(response, status=status.HTTP_200_OK)
        except LMSException as e:
            response = account_utils.manage_response(status=False,
                                            message=e.message,
                                            log=e.message, logger_obj=logger)
            return Response(response, e.status_code, content_type="application/json")
        except Exception as e:
            response = account_utils.manage_response(status=False,
                                            message="Something went wrong.Please try again",
                                            log=str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddPerformanceInfo:
    pass