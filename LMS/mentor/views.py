import logging,os
from account.models import User, Role
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from account.decorators import user_login_required
from account.serializers import RegisterSerializer
from account.utils import Util
from .models import Mentor
from .serializers import MentorSerializer
from LMS.utils import ExceptionType, LMSException


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')

file_handler = logging.FileHandler(os.path.abspath("loggers/log_mentors.log"))
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


@method_decorator(user_login_required,name='dispatch')
class AdminView(APIView):

    def get(self,*args,**kwargs):
        """[displays specific/all mentors' personal details and courses]
            args: kwargs[pk]: user id of the mentor
            Returns:
                Response: status , message and data
                @type: status: Boolean, message:str, data: list
        """
        try:
            current_user_id = kwargs.get('userid')
            print(User.objects.get(id=current_user_id).role)
            if User.objects.get(id=current_user_id).role.__str__() == "admin":
                print(kwargs.get('pk'))
                if(kwargs.get('pk')):
                    mentor_user = User.objects.filter(id=kwargs.get('pk')).first()
                    #if not mentor_user or mentor_user.role.__ne__('mentor'):
                    if not mentor_user or mentor_user.role.__str__() != 'mentor':
                        raise LMSException(ExceptionType.NonExistentError,"Sorry,no mentor with this id exists.")
                    mentor=Mentor.objects.filter(user=kwargs.get('pk')).first()
                    serializer = MentorSerializer(mentor)
                    response = Util.manage_response(status=True,
                                                    message="Retrieved mentor", data=serializer.data,
                                                    log="Retrieved mentor with id {}".format(kwargs.get('pk')), logger_obj=logger)
                    return Response(response, status=status.HTTP_200_OK, content_type="application/json")

                mentors = Mentor.objects.all()
                serializer = MentorSerializer(mentors,many=True)
                response = Util.manage_response(status=True,
                                                message="Retrieved list of mentors",data=serializer.data,
                                                log="Retrieved list of mentors", logger_obj=logger)
                return Response(response, status=status.HTTP_200_OK, content_type="application/json")

            else:
                raise LMSException(ExceptionType.UnauthorizedError, "You are not authorized to perform this operation.")

        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=e.message, logger_obj=logger)
            return Response(response, status.HTTP_404_NOT_FOUND, content_type="application/json")

        except Exception as e:
            response = Util.manage_response(status=False,
                                            message=str(e),
                                            log=str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST, content_type="application/json")



@method_decorator(user_login_required,name='dispatch')
class MentorProfile(APIView):

    def get(self,*args,**kwargs):
        """[displays mentor's personal details and courses]
            args: kwargs[pk]: user id of the mentor
            Returns:
                Response: status , message and data
                @type: status: Boolean, message:str, data: list
        """
        try:
            current_user_id = kwargs.get('userid')
            user= User.objects.get(id=current_user_id)
            if user.role.__str__() != 'mentor':
                raise LMSException(ExceptionType.UnauthorizedError, "You are not authorized to perform this operation.")

            mentor = Mentor.objects.get(user=current_user_id)
            serializer = MentorSerializer(mentor)
            response = Util.manage_response(status=True,
                                            message="Retrieved mentor details", data=serializer.data,
                                            log="Retrieved mentor with id {}".format(kwargs.get('pk')),
                                            logger_obj=logger)
            return Response(response, status=status.HTTP_200_OK, content_type="application/json")
        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=e.message, logger_obj=logger)
            return Response(response, status.HTTP_404_NOT_FOUND, content_type="application/json")

        except Exception as e:
            response = Util.manage_response(status=False,
                                            message=str(e),
                                            log=str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST, content_type="application/json")

    def post(self,request,*args,**kwargs):
        """[create User for user by taking in user details]

            :param kwargs: [mandatory]:[string]dictionary containing requesting user's id generated from decoded token
            :param request:[mandatory]: name,email,role,phone_number of user to be created
            :return:creation confirmation and status code.Email is sent to host email User.
        """

        try:
            current_user_id = kwargs.get('userid')
            user = User.objects.get(id=current_user_id)
            if user.role.__str__() != 'mentor':
                raise LMSException(ExceptionType.UnauthorizedError, "You are not authorized to perform this operation.")
            if Mentor.objects.get(user=current_user_id):
                raise LMSException(ExceptionType.MentorExists, "An account with this user already exists.")

            request.POST._mutable = True        #TODO:take course name from postman and set course id
            request.data["user"] = kwargs['userid']
            request.POST._mutable = False
            serializer = MentorSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Util.manage_response(status=True,
                                            message='Profile details added successfully.',
                                            log='Profile details added successfully.', logger_obj=logger)
            return Response(response, status=status.HTTP_200_OK)

        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=e.message, logger_obj=logger)
            return Response(response, status.HTTP_404_NOT_FOUND, content_type="application/json")

        except Exception as e:
            response = Util.manage_response(status=False,
                                            message="Something went wrong.Please try again",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")


    def patch(self,request,**kwargs):  #args
        """[update mentor personal details or courses taken]

            :param kwargs: [mandatory]:[string]dictionary containing requesting user's id generated from decoded token
            :param request:[optional]: one or more fields among name,email,phone_number,courses of mentor
            :return:updation confirmation and status code.
        """
        try:
            current_user_id = kwargs.get('userid')
            user = User.objects.get(id=current_user_id)
            if user.role.__str__() != 'mentor':
                raise LMSException(ExceptionType.UnauthorizedError, "You are not authorized to perform this operation.")
            # If update contains 'role' update.
            mentor = Mentor.objects.get(user=current_user_id)
            if request.data.get('role'):
                raise LMSException(ExceptionType.UnauthorizedError, "You are not allowed to change your role.Please contact admin.")

            data = request.data
            if 'name' or 'phone_number' or 'email' in data:
                serializer = RegisterSerializer(user, data=request.data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
            if 'course' in data:
                serializer = MentorSerializer(mentor,data=request.data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
            user_data = serializer.data
            response = Util.manage_response(status=True,
                                            message='Updated successfully.', data=user_data,
                                            log='Updated user record successfully.', logger_obj=logger)

            return Response(response, status=status.HTTP_200_OK)
        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=e.message, logger_obj=logger)
            return Response(response, status.HTTP_404_NOT_FOUND, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False,
                                            message="Something went wrong.Please try again",
                                            log=str(e), logger_obj=logger)
            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")


#TODO:add more than one course object in profile[collaborator ref]
#TODO: in mentor dashboard get view use Loginredirecturl:name of course,no.of students enrolled
#TODO: mentor settings shows personal details and course name.,patch,delete course|phone_number
#TODO:student detail page post,patch,get.Student detail has fields: student id(Student table),student name(User),course id(Course)
#course name(Course),current score,assessment date,mentor name(Mentor table->user)
#Student.objects.filter(course='python').count()