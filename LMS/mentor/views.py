import logging, os
from account.models import User
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from account.decorators import user_login_required
from account.utils import Util
from course.models import Course
from services.logging import loggers
from .models import Mentor
from .serializers import MentorSerializer
from LMS.utils import ExceptionType, LMSException

logger = loggers("loggers", "log_mentors.log")


@method_decorator(user_login_required, name='dispatch')
class AdminView(generics.GenericAPIView):
    serializer_class = MentorSerializer

    def get_queryset(self):
        pass

    def get(self, request, **kwargs):
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
                serializer = MentorSerializer(mentors, many=True)
                response = Util.manage_response(status=True,
                                                message="Retrieved list of mentors", data=serializer.data,
                                                log="Retrieved list of mentors", logger_obj=logger)
                return Response(response, status=status.HTTP_200_OK, content_type="application/json")

            else:
                raise LMSException(ExceptionType.UnauthorizedError, "You are not authorized to perform this operation.",
                                   status.HTTP_401_UNAUTHORIZED)

        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=e.message, logger_obj=logger)
            return Response(response, e.status_code, content_type="application/json")

        except Exception as e:
            response = Util.manage_response(status=False,
                                            message=str(e),
                                            log=str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST, content_type="application/json")


@method_decorator(user_login_required, name='dispatch')
class MentorProfile(generics.GenericAPIView):
    serializer_class = MentorSerializer

    queryset = Mentor.objects.all()


    def get(self, request, **kwargs):
        """[displays mentor's personal details and courses.]
            args: kwargs[pk]: user id of the mentor
            Returns:
                Response: status , message and data
                @type: status: Boolean, message:str, data: list
        """
        try:

            get_user_id = kwargs.get('pk')  # id whose details the requesting user[admin/mentor] is seeking
            current_user_id = kwargs.get('userid')  # id of requesting user
            current_user_role = kwargs.get('role')  # role of requesting user

            if current_user_role != 'admin' and get_user_id != current_user_id:
                raise LMSException(ExceptionType.UnauthorizedError, "You are not authorized to perform this operation.",
                                   status.HTTP_401_UNAUTHORIZED)

            logger.info("checking for mentor with matching userid retrieved from pk")
            mentor = Mentor.objects.filter(user=get_user_id).first()
            if not mentor:  # if user account of mentor exists but mentor object doesn't
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

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")

        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=e.message, logger_obj=logger)
            return Response(response, e.status_code, content_type="application/json")

        except Exception as e:
            response = Util.manage_response(status=False,
                                            message=str(e),
                                            log=str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST, content_type="application/json")

    def post(self, request, **kwargs):
        """[create mentor profile object for mentor  by taking in course and user details]

            :param kwargs: [mandatory]:[string]dictionary containing requesting user's id generated from decoded token
            :param request:[mandatory]: name of course and mentor's email.
            :return:creation confirmation and status code.
        """

        try:
            current_user_role = kwargs.get('role')
            if current_user_role != 'admin':
                raise LMSException(ExceptionType.UnauthorizedError, "You are not authorized to perform this operation.",
                                   status.HTTP_401_UNAUTHORIZED)

            request.POST._mutable = True

            user = User.objects.filter(email=request.data['user']).first()
            if not user:  # if user with this email isn't in database

                raise LMSException(ExceptionType.NonExistentError, "No such user record found.",
                                   status.HTTP_404_NOT_FOUND)
            if Mentor.objects.filter(user=user.id):  # if a mentor object is already existing for this user
                raise LMSException(ExceptionType.MentorExists, "An account with this user already exists.",
                                   status.HTTP_400_BAD_REQUEST)

            request.data["user"] = user.id

            course = Course.objects.filter(name=request.data["course"]).first()
            if not course:
                raise Course.DoesNotExist('No such course exists')

            request.data["course"] = course.id

            request.POST._mutable = False

            serializer = MentorSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Util.manage_response(status=True,
                                            message='Profile details added successfully.', data=serializer.data,
                                            log='Profile details added successfully.', logger_obj=logger)
            return Response(response, status=status.HTTP_200_OK)

        except Course.DoesNotExist as e:
            response = Util.manage_response(status=False,
                                            message="Requested course does not exist",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")

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

    def delete(self, request, **kwargs):
        """[soft deletes mentor profile object for mentor  by taking in id]

            :param kwargs: [mandatory]:[string]dictionary containing requesting user's id and role generated from decoded token
            :return:deletion confirmation and status code.
        """
        try:
            current_user_role = kwargs.get('role')
            delete_mentor = User.objects.filter(id=kwargs.get('pk')).exclude(is_deleted=True).first()
            if current_user_role != 'admin':  # if requesting user isn't admin
                raise LMSException(ExceptionType.UnauthorizedError, "You are not authorized to perform this operation.",
                                   status.HTTP_401_UNAUTHORIZED)
            if not delete_mentor:  # if user to be deleted isn't in database
                raise LMSException(ExceptionType.NonExistentError, "No such user record found.",
                                   status.HTTP_404_NOT_FOUND)

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
