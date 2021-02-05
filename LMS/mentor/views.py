from account.models import User, Role
from rest_framework import status, generics
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from account.decorators import user_login_required
from account.serializers import RegisterSerializer
from account.utils import Util
from rest_framework.parsers import FileUploadParser,MultiPartParser
from course.models import Course
from services.logging import loggers
from .models import Mentor
from .serializers import MentorSerializer, MentorPostSerializer
from LMS.utils import ExceptionType, LMSException, admin_only

logger = loggers("log_mentors.log")


@method_decorator(user_login_required, name='dispatch')
class AdminView(generics.GenericAPIView):
    serializer_class = MentorSerializer
    queryset = User.objects.all()

    @admin_only
    def get(self, request, **kwargs):
        """[displays all mentors' personal details and courses]
            args: kwargs[pk]: user id of the mentor
            Returns:
                Response: status , message and data
                @type: status: Boolean, message:str, data: list
        """
        try:
            mentors = Mentor.objects.all()
            logger.info('retrieving all existing mentors')
            serializer = MentorSerializer(mentors, many=True)
            response = Util.manage_response(status=True,
                                            message="Retrieved list of mentors", data=serializer.data,
                                            log="Retrieved list of mentors", logger_obj=logger)
            return Response(response, status=status.HTTP_200_OK, content_type="application/json")


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


@method_decorator(user_login_required, name='dispatch')
class MentorProfile(generics.GenericAPIView):
    serializer_class = MentorSerializer
    queryset = User.objects.all()

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
            logger.info('retrieving existing mentor with incoming id')
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

    def patch(self, request, **kwargs):
        try:
            current_user_role = kwargs.get('role')
            update_mentor = Mentor.objects.filter(user=kwargs.get('pk')).first()
            if current_user_role != 'admin':  # if requesting user isn't admin
                raise LMSException(ExceptionType.UnauthorizedError, "You are not authorized to perform this operation.",
                                   status.HTTP_401_UNAUTHORIZED)
            if not update_mentor:  # if user to be updated isn't in database
                raise LMSException(ExceptionType.NonExistentError, "No such mentor record found.",
                                   status.HTTP_404_NOT_FOUND)
            if 'user' in request.data:
                raise LMSException(ExceptionType.UnauthorizedError, "Sorry,user id update is not permitted.",
                                   status.HTTP_401_UNAUTHORIZED)

            for course_id in request.data["course"]:
                course = Course.objects.filter(id=course_id).first()
                if not course:
                    raise Course.DoesNotExist('No such course exists')
            serializer = MentorSerializer(update_mentor, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            logger.info('updating existing mentor with incoming courses')
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

    @admin_only
    def delete(self, request, **kwargs):
        """[soft deletes mentor profile object for mentor  by taking in id]

            :param kwargs: [mandatory]:[string]dictionary containing requesting user's id and role generated from decoded token
            :return:deletion confirmation and status code.
        """
        try:
            delete_mentor = User.objects.filter(id=kwargs.get('pk')).exclude(is_deleted=True).first()
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


@method_decorator(user_login_required, name='dispatch')
class CreateMentor(generics.GenericAPIView):
    parser_classes = (MultiPartParser,)
    serializer_class = MentorPostSerializer
    queryset = User.objects.all()

    @admin_only
    def post(self, request, **kwargs):
        """[create mentor profile object for mentor  by taking in course id and user email]

            :param kwargs: [mandatory]:[string]dictionary containing requesting user's id generated from decoded token
            :param request:[mandatory]: name[string],email[string],role[integer],phone_number[string],course[list of integer ids] of mentor to be created
            :return:creation confirmation and status code.
        """

        try:
            course_list=request.data['course']
            error = []
            valid_list=[]

            for course_id in course_list:
                if not Course.objects.filter(id=course_id).first():
                    error.append(course_id+" is not a valid course id and hence could not be processed.")
                else:
                    valid_list.append(course_id)


            if len(valid_list) == 0:
                raise Course.DoesNotExist('Please enter at least one valid course id')
            request.data['course']=valid_list

            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                logger.info('posting new mentor user with incoming details')
                user = serializer.save()
            Util.send_email(user)

            request.POST._mutable = True
            request.data["user"] = user.id
            request.POST._mutable = False
            serializer = MentorSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            logger.info('posting new mentor with incoming details')
            serializer.save()

            response = Util.manage_response(status=True,error=error,
                                            message='Profile details added successfully.', data=serializer.data,
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
