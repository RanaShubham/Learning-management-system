import datetime
import logging
import os

import jwt
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_str
from LMS.utils import ExceptionType, LMSException
from rest_framework import generics, permissions, serializers, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from services.cache import Cache
from services.encrypt import Encrypt

from .decorators import user_login_required
from .models import Role, User
from .serializers import *
from .utils import Util

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')

file_handler = logging.FileHandler(os.path.abspath("loggers/log_accounts.log"))
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


@method_decorator(user_login_required, name='dispatch')
class RegisterUser(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    def get_queryset(self):
        pass
    def get(self, request, **kwargs):
        """[To get all the registered User details when logged in as admin.]

        :param kwargs: [mandatory]:[string]dictionary containing requesting user's id generated from decoded token
        :return:Response with status of success and data if successful.
        """
        try:
            current_user_id = kwargs.get('userid')
            if User.objects.get(id=current_user_id).role.role_id != Role.objects.get(role='admin').role_id:
                raise LMSException(ExceptionType.UnauthorizedError,"You are not authorized to perform this operation.",status.HTTP_401_UNAUTHORIZED)

            logger.info('retrieving list of registered users')
            users = User.objects.filter(is_deleted=False)
            serializer = RegisterSerializer(users, many=True)
            response = Util.manage_response(status=True, message='Retrieved all users.', data=serializer.data,
                                            log='retrieved users', logger_obj=logger)
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
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, **kwargs):
        """[create User for user by taking in user details]

        :param kwargs: [mandatory]:[string]dictionary containing requesting user's id generated from decoded token
        :param request:[mandatory]: name,email,role,phone_number of user to be created
        :return:creation confirmation and status code.Email is sent to host email User.
        """

        try:
            requesting_user_id = kwargs.get('userid')
            requesting_user_role = User.objects.get(id=requesting_user_id).role
            if requesting_user_role.role_id != Role.objects.get(role='admin').role_id:
                raise LMSException(ExceptionType.UnauthorizedError,"You are not authorized to perform this operation.",status.HTTP_401_UNAUTHORIZED)

            normalized_admission_role = request.data['role'].lower()

            admission_role_obj = Role.objects.filter(role=normalized_admission_role).first()

            if not admission_role_obj:
                raise LMSException(ExceptionType.RoleError, "{} is not a valid role.".format(normalized_admission_role),status.HTTP_400_BAD_REQUEST)

            request.POST._mutable = True
            request.data['role'] = admission_role_obj.pk
            request.POST._mutable = False
            logger.info('posting new user with incoming details')
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            user = User.objects.get(email=request.data.get('email'))
            Util.send_email(user)
            response = Util.manage_response(status=True, message='Registered successfully.Login Credentials have been sent to your email.',
                                            log='Registered successfully.Login credentials sent.', logger_obj=logger)
            return Response(response, status=status.HTTP_201_CREATED)

        except KeyError as e:
            result = {'status': False, 'message':"Please specify a role for the user to be registered."}
            return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except LMSException as e:
            response = Util.manage_response(status=False,
                                            message=e.message,
                                            log=e.message, logger_obj=logger)
            return Response(response, e.status_code, content_type="application/json")

        except serializers.ValidationError as e:
            response = Util.manage_response(status=False,
                                            message=e.detail,
                                            log=e.detail, logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False,
                                            message="Something went wrong.Please try again",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")



    def patch(self,request,**kwargs):
        """[updates a user's one or more credentials]

        :param kwargs: [mandatory]:[string]dictionary containing requesting user's id generated from decoded token
        :return:updation confirmation, new details and status code
        """

        try:
            current_user_id = kwargs.get('userid')
            current_user_role = kwargs.get('role')
            update_user = User.objects.filter(id=kwargs.get('pk')).exclude(is_deleted=True).first()
            if not update_user:  # if user to be updated isn't in database
                raise LMSException(ExceptionType.NonExistentError, "No such user record found.",status.HTTP_404_NOT_FOUND)

            if current_user_role != 'admin' and str(current_user_id) != kwargs.get('pk'): #if user is not admin and if the record id(pk) he seeks to update doesn't match his own id
                raise LMSException(ExceptionType.UnauthorizedError,"Sorry,you are not authorized to update other user's credentials.",status.HTTP_401_UNAUTHORIZED)

            if request.data.get('role'):
                raise LMSException(ExceptionType.UnauthorizedError,"Sorry,you are not authorized to update role.Please contact admin.",status.HTTP_401_UNAUTHORIZED)

            logger.info('updating existing user with incoming details')
            serializer = RegisterSerializer(update_user, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            user_data = serializer.data
            response = Util.manage_response(status=True,
                                            message='Updated successfully.',data=user_data,
                                            log='Updated user record successfully.', logger_obj=logger)
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

    def delete(self, request, pk, **kwargs):
        """[sets current user's is_deleted flag to false]

        :param kwargs: [mandatory]:[string]dictionary containing user id generated from decoded token
        :return:deletion confirmation and status code
        """
        try:
            current_user_id = kwargs['userid']
            if User.objects.get(id=current_user_id).role.role_id != Role.objects.get(role='admin').role_id:
                raise LMSException(ExceptionType.UnauthorizedError, "You are not authorized to perform this operation.",status.HTTP_401_UNAUTHORIZED)

            if not User.objects.filter(id=pk).exclude(is_deleted=True).exists():
                raise LMSException(ExceptionType.NonExistentError, "Requested user does not exist",status.HTTP_404_NOT_FOUND)
            else:
                logger.info('deleting existing user with given id')
                user = User.objects.get(id=pk)
                user.soft_delete()
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


class LoginUser(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def get_queryset(self):
        pass
    def post(self, request):
        """[gets user with matching credentials and generates authentication token using id and time]

        :return:login confirmation, authentication token containing user id and status code
        """
        try:

            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            logger.info('checking existing user with given email')
            user = User.objects.get(email=serializer.data['email'])
            current_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            token = Encrypt.encode(user.id,user.role.role, current_time)
            Cache.getInstance().set("TOKEN_" + str(user.id) + "_AUTH", token)
            result = Util.manage_response(status=True,
                                            message='Token generated.Login successful.',
                                            log='Token generated.Login successful.', logger_obj=logger)

            response = Response(result, status=status.HTTP_200_OK, content_type="application/json")
            response.__setitem__(header="HTTP_AUTHORIZATION", value=token)
            return response
        except User.DoesNotExist as e:
            response = Util.manage_response(status=False,
                                            message="User does not exist",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except AuthenticationFailed as e:
            response = Util.manage_response(status=False,
                                            message="Invalid credentials",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_401_UNAUTHORIZED, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False,
                                            message="Something went wrong.Please try again",
                                            log=str(e), logger_obj=logger)

            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")

    @method_decorator(user_login_required, name='dispatch')
    def get(self, request, **kwargs):
        """[deletes current user's token from cache]

        :param kwargs: [mandatory]:[string]authentication token containing user id
        :return:log out confirmation and status code
        """
        try:
            cache = Cache.getInstance()
            current_user = kwargs['userid']
            logger.info("checking for requesting user's token record in cache ")
            if cache.get("TOKEN_" + str(current_user) + "_AUTH"):
                cache.delete("TOKEN_" + str(current_user) + "_AUTH")
            response = Util.manage_response(status=True,
                                          message='Logged out',
                                          log='Logged out', logger_obj=logger)

            return Response(response, status=status.HTTP_200_OK, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False,
                                            message="Something went wrong.Please try again",
                                            log=str(e), logger_obj=logger)
            return Response(response, status.HTTP_400_BAD_REQUEST, content_type="application/json")



class RequestPasswordResetEmail(generics.GenericAPIView):
    """[sends an email to facilitate password reset]
    """
    serializer_class = ResetPasswordEmailRequestSerializer
    def get_queryset(self):
        pass
    def post(self, request, **kwargs):
        """[sends an email to facilitate password reset]
        :param request: [mandatory]:[string]:email of user
        :return: [string] confirmation message
                 email with link to reset password
                 [int] status code
        """
        try:
            email = request.data.get('email', '')
            logger.info("checking for user with given email ")
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                current_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                token = force_str(Encrypt.encode_reset(user.id, current_time))
                Cache.getInstance().set("RESET_" + str(user.id) + "_TOKEN", token)
                redirect_url = reverse('account:reset_password', kwargs={'reset_token': token})
                url = request.build_absolute_uri(redirect_url)
                email_body = 'Hello, please click on the link below and enter new password when asked for\n' + url
                data = {'email_body': email_body, 'to_email': user.email, 'email_subject': 'Reset your passsword'}
                Util.send_reset_email(data)
                result = Util.manage_response(status=True,
                                              message='We have sent you a link to reset your password',
                                              log='We have sent you a link to reset your password', logger_obj=logger)
                return Response(result, status=status.HTTP_200_OK, content_type="application/json")
            else:
                result = Util.manage_response(status=True,
                                              message="Email id you have entered doesn't exist",
                                              log="Email id you have entered doesn't exist", logger_obj=logger)
                return Response(result, status=status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except Exception as e:
            response = Util.manage_response(status=False,
                                            message="Something went wrong.Please try again",
                                            log=str(e), logger_obj=logger)
            return Response(response, status=status.HTTP_400_BAD_REQUEST, content_type="application/json")



class SetNewPassword(generics.GenericAPIView):
    """[returns new password when supplied with uid,token and new password]
    """
    serializer_class = SetNewPasswordSerializer
    def get_queryset(self):
        pass
    def patch(self, request, **kwargs):
        """[returns new password when supplied with uid,token and new password]

        :param request: [mandatory]:[string]: new password
        :return: confirmation message and status code
        """
        try:
            password = request.data.get('password')
            token = kwargs.get('reset_token')
            id = Encrypt.decode(token).get('id')
            cached_reset_token = force_str(Cache.getInstance().get("RESET_" + str(id) + "_TOKEN"))
            if cached_reset_token == 'None':
                raise LMSException(ExceptionType.UnauthorizedError, "reset password url is expired.",status.HTTP_401_UNAUTHORIZED)
            if cached_reset_token != token:
                raise LMSException(ExceptionType.UnauthorizedError, "reset password url is invalid.",status.HTTP_400_BAD_REQUEST)
            if not password or len(password) <= 2:
                raise LMSException(ExceptionType.UserException, "Please provide a appropirate password with atleast 3 character.",status.HTTP_400_BAD_REQUEST)
            logger.info("checking for user matching id retrieved from token")
            user = User.objects.get(id=id)
            user.set_password(password)
            user.save()
            Cache.getInstance().delete("RESET_" + str(id) + "_TOKEN")
            result = Util.manage_response(status=True,
                                          message='Password reset successful',
                                          log='Password reset successful', logger_obj=logger)
            return Response(result, status=status.HTTP_200_OK, content_type="application/json")
        except jwt.exceptions.InvalidSignatureError as e:
            response = Util.manage_response(status=False,
                                            message='reset password url is corrupt.',
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
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR,content_type="application/json")
