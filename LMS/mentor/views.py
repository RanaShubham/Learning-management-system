import logging,os
from account.models import User, Role
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from account.decorators import user_login_required
from account.serializers import RegisterSerializer
from account.utils import Util
from course.models import Course
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
class AdminView(generics.GenericAPIView):

    serializer_class = MentorSerializer
    queryset = User.objects.all()
    def get(self,request,**kwargs):
        """[displays all mentors' personal details and courses]
            args: kwargs[pk]: user id of the mentor
            Returns:
                Response: status , message and data
                @type: status: Boolean, message:str, data: list
        """
        try:
            current_user_id = kwargs.get('userid')
            if User.objects.get(id=current_user_id).role.__str__() == "admin":
                mentors = Mentor.objects.all()
                serializer = MentorSerializer(mentors,many=True)
                response = Util.manage_response(status=True,
                                                message="Retrieved list of mentors",data=serializer.data,
                                                log="Retrieved list of mentors", logger_obj=logger)
                return Response(response, status=status.HTTP_200_OK, content_type="application/json")

            else:
                raise LMSException(ExceptionType.UnauthorizedError, "You are not authorized to perform this operation.",status.HTTP_401_UNAUTHORIZED)

        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=e.message, logger_obj=logger)
            return Response(response, e.status_code, content_type="application/json")

        except Exception as e:
            response = Util.manage_response(status=False,
                                            message='Something went wrong.Please try again.',
                                            log=str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST, content_type="application/json")


@method_decorator(user_login_required,name='dispatch')
class MentorProfile(generics.GenericAPIView):

    serializer_class = MentorSerializer
    queryset = User.objects.all()
    def get(self,request,**kwargs):
        """[displays mentor's personal details and courses.]
            args: kwargs[pk]: user id of the mentor
            Returns:
                Response: status , message and data
                @type: status: Boolean, message:str, data: list
        """
        try:
            get_user_id = kwargs.get('pk') #id whose details the requesting user[admin/mentor] is seeking
            current_user_id = kwargs.get('userid') #id of requesting user
            current_user_role = kwargs.get('role') #role of requesting user

            if current_user_role != 'admin' and get_user_id != current_user_id:
                raise LMSException(ExceptionType.UnauthorizedError, "You are not authorized to perform this operation.",status.HTTP_401_UNAUTHORIZED)

            logger.info("checking for mentor with matching userid retrieved from pk")
            mentor = Mentor.objects.filter(user=get_user_id).first()
            if not mentor: #if user account of mentor exists but mentor object doesn't
                raise Mentor.DoesNotExist('No such mentor exists')
            serializer = MentorSerializer(mentor)
            response = Util.manage_response(status=True,
                                            message="Retrieved mentor details", data=serializer.data,
                                            log="Retrieved mentor with id {}".format(kwargs.get('pk')),
                                            logger_obj=logger)
            return Response(response, status=status.HTTP_200_OK, content_type="application/json")
        except Mentor.DoesNotExist as e:
            response = Util.manage_response(status=False,
                                            message="Requested mentor profile does not exist",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_404_NOT_FOUND, content_type="application/json")

        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=e.message, logger_obj=logger)
            return Response(response, e.status_code, content_type="application/json")

        except Exception as e:
            response = Util.manage_response(status=False,
                                            message='Something went wrong.Please try again.',
                                            log=str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST, content_type="application/json")

    def patch(self,request,**kwargs):
        try:
            current_user_role = kwargs.get('role')
            update_mentor = Mentor.objects.filter(user=kwargs.get('pk')).first()
            if current_user_role != 'admin':  # if requesting user isn't admin
                raise LMSException(ExceptionType.UnauthorizedError, "You are not authorized to perform this operation.",
                                   status.HTTP_401_UNAUTHORIZED)
            if not update_mentor:  # if user to be updated isn't in database
                raise LMSException(ExceptionType.NonExistentError, "No such mentor record found.", status.HTTP_404_NOT_FOUND)
            if 'user' in request.data:
                raise LMSException(ExceptionType.UnauthorizedError, "Sorry,user id update is not permitted.",status.HTTP_401_UNAUTHORIZED)

            for course_id in request.data["course"]:
                course = Course.objects.filter(id=course_id).first()
                if not course:
                    raise Course.DoesNotExist('No such course exists')
            serializer = MentorSerializer(update_mentor,data=request.data,partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()

            response = Util.manage_response(status=True,
                                            message='Course details updated successfully.', data=serializer.data,
                                            log='Course details updated successfully.', logger_obj=logger)
            return Response(response, status=status.HTTP_200_OK)
        except Course.DoesNotExist as e:
            response = Util.manage_response(status=False,
                                            message="Requested course does not exist",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_404_NOT_FOUND, content_type="application/json")
        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=e.message, logger_obj=logger)

            return Response(response, e.status_code, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False,
                                            message="Something went wrong.Please try again",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")

    def delete(self,request,**kwargs):
        """[soft deletes mentor profile object for mentor  by taking in id]

            :param kwargs: [mandatory]:[string]dictionary containing requesting user's id and role generated from decoded token
            :return:deletion confirmation and status code.
        """
        try:
            current_user_role = kwargs.get('role')
            delete_mentor = User.objects.filter(id=kwargs.get('pk')).exclude(is_deleted=True).first()
            if current_user_role != 'admin':  # if requesting user isn't admin
                raise LMSException(ExceptionType.UnauthorizedError, "You are not authorized to perform this operation.",status.HTTP_401_UNAUTHORIZED)
            if not delete_mentor:  # if user to be deleted isn't in database
                raise LMSException(ExceptionType.NonExistentError, "No such user record found.",status.HTTP_404_NOT_FOUND)

            logger.info('deleting existing mentor with given id')
            delete_mentor.soft_delete()
            response = Util.manage_response(status=True,
                                            message='Deleted successfully.',
                                            log='Deleted user record successfully.', logger_obj=logger)
            return Response(response, status=status.HTTP_200_OK)
        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=e.message, logger_obj=logger)

            return Response(response, e.status_code, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False,
                                            message="Something went wrong.Please try again",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")

@method_decorator(user_login_required, name='dispatch')
class CreateMentor(generics.GenericAPIView):

    serializer_class = MentorSerializer
    queryset = User.objects.all()

    def post(self,request,**kwargs):
        """[create mentor profile object for mentor  by taking in course id and user email]

            :param kwargs: [mandatory]:[string]dictionary containing requesting user's id generated from decoded token
            :param request:[mandatory]: id of course and mentor's email.
            :return:creation confirmation and status code.
        """

        try:
            current_user_role = kwargs.get('role')
            if current_user_role != 'admin':
                raise LMSException(ExceptionType.UnauthorizedError, "You are not authorized to perform this operation.",status.HTTP_401_UNAUTHORIZED)
            for course_id in request.data["course"]:
                course = Course.objects.filter(id=course_id).first()
                if not course:
                    raise Course.DoesNotExist('No such course exists')

            normalized_admission_role = request.data['role'].lower()
            admission_role_obj = Role.objects.filter(role=normalized_admission_role).first()
            if not admission_role_obj:
                raise LMSException(ExceptionType.RoleError, "{} is not a valid role.".format(normalized_admission_role),
                                   status.HTTP_400_BAD_REQUEST)

            request.POST._mutable = True
            request.data['role'] = admission_role_obj.pk
            request.POST._mutable = False

            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user=serializer.save()
            Util.send_email(user)

            request.POST._mutable = True
            request.data["user"] = user.id
            request.POST._mutable = False

            serializer = MentorSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            response = Util.manage_response(status=True,
                                            message='Profile details added successfully.',data=serializer.data,
                                            log='Profile details added successfully.', logger_obj=logger)
            return Response(response, status=status.HTTP_201_CREATED)

        except Course.DoesNotExist as e:
            response = Util.manage_response(status=False,
                                            message="Requested course does not exist",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_404_NOT_FOUND, content_type="application/json")

        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=e.message, logger_obj=logger)
            return Response(response, e.status_code, content_type="application/json")

        except Exception as e:
            response = Util.manage_response(status=False,
                                            message="Something went wrong.Please try again",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")



