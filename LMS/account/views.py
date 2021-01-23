import datetime
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from .serializers import LoginSerializer,RegisterSerializer,ResetPasswordEmailRequestSerializer,SetNewPasswordSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from .decorators import user_login_required
from .models import User
from services.encrypt import Encrypt
from services.cache import Cache
from .utils import Util
from rest_framework import serializers
from LMS.utils import ExceptionType, LMSException


@method_decorator(user_login_required, name='dispatch')
class RegisterUser(APIView):

    def get(self, request,**kwargs):
        """[To get all the registered User details when logged in as admin.]

        :param kwargs: [mandatory]:[string]dictionary containing requesting user's id generated from decoded token
        :return:Response with status of success and data if successful.
        """
        try:
            current_user_id = kwargs.get('userid')
            if not (User.objects.get(id=current_user_id).role == 'admin'):
                raise LMSException(ExceptionType.UnauthorizedError,"Sorry,you are not authorized to perform this operation.")

            users = User.objects.filter(is_deleted=False)
            serializer = RegisterSerializer(users, many=True)
            response = {'status': True,
                        'message': 'Retrieved all users.','data':serializer.data}
            return Response(response, status=status.HTTP_200_OK)
        except LMSException as e:
            result = {'status': False, 'message': e.message}
            return Response(result, status.HTTP_404_NOT_FOUND, content_type="application/json")
        except User.DoesNotExist:
            response = {'status': False, 'message': 'Please login again.'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            response = {'status':False, 'message':'Somethign went wrong.'}
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, **kwargs):
        """[create User for user by taking in user details]

        :param kwargs: [mandatory]:[string]dictionary containing requesting user's id generated from decoded token
        :param request:[mandatory]: name,email,role,phone_number of user to be created
        :return:creation confirmation and status code.Email is sent to host email User.
        """

        try:
            current_user_id = kwargs.get('userid')
            if not (User.objects.get(id=current_user_id).role == 'admin'):
                raise LMSException(ExceptionType.UnauthorizedError,"Sorry,you are not authorized to perform this operation.")

            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            user_data = serializer.data
            user = User.objects.get(email=user_data['email'], name=user_data['name'],
                                    phone_number=user_data['phone_number'], role=user_data['role'])
            Util.send_email(user)
            response = {'status': True,
                        'message': 'Registered successfully. Login Credentials have been sent to your email.'}
            return Response(response, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            result = {'status': False, 'message': e.detail}
            return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except Exception as e:
            result = {'status': False, 'message': 'Some other issue.Please try again.'}
            return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")



    def patch(self,request,pk,**kwargs):
        """[updates a user's one or more credentials]

        :param kwargs: [mandatory]:[string]dictionary containing requesting user's id generated from decoded token
        :return:updation confirmation, new details and status code
        """

        try:
            current_user_id = kwargs.get('userid')
            if not (User.objects.get(id=current_user_id).role == 'admin'):
                raise LMSException(ExceptionType.UnauthorizedError,"Sorry,you are not authorized to perform this operation.")

            if not User.objects.filter(id=pk).exclude(is_deleted=True).exists():
                raise LMSException(ExceptionType.NonExistentError, "Requested user does not exist")
            user = User.objects.get(id=pk)
            serializer = RegisterSerializer(user, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            user_data = serializer.data
            response = {'status': True,
                        'message': 'Updated successfully.','data':user_data}
            return Response(response, status=status.HTTP_200_OK)
        except LMSException as e:
            result = {'status': False, 'message': e.message}
            return Response(result, status.HTTP_404_NOT_FOUND, content_type="application/json")
        except Exception as e:
            result = {'status': False, 'message': 'Some other issue.Please try again'}
            return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")


    def delete(self, request, pk, **kwargs):
        """[sets current user's is_deleted flag to false]

        :param kwargs: [mandatory]:[string]dictionary containing user id generated from decoded token
        :return:deletion confirmation and status code
        """
        try:
            current_user_id = kwargs['userid']
            if not (User.objects.get(id=current_user_id).role == 'admin'):
                raise LMSException(ExceptionType.UnauthorizedError, "Sorry,you are not authorized to perform this operation.")

            if not User.objects.filter(id=pk).exclude(is_deleted=True).exists():
                raise LMSException(ExceptionType.NonExistentError, "Requested user does not exist")
            else:
                user = User.objects.get(id=pk)
                user.soft_delete()
            response = {'status': True,
                        'message': 'Deleted successfully.'}
            return Response(response, status=status.HTTP_200_OK)

        except LMSException as e:
            result = {'status': False, 'message': e.message}
            return Response(result, status.HTTP_404_NOT_FOUND, content_type="application/json")
        except Exception as e:
            result = {'status': False, 'message': 'Some other issue.Please try again'}
            return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")


class LoginUser(APIView):

    def post(self, request):
        """[gets user with matching credentials and generates authentication token using id and time]

        :return:login confirmation, authentication token containing user id and status code
        """
        try:

            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = User.objects.get(email=serializer.data['email'])
            current_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            token = Encrypt.encode(user.id, current_time)
            Cache.getInstance().set("TOKEN_" + str(user.id) + "_AUTH", token)
            result = {'status':True, 'message':'Token generated.Login successful.'}
            response = Response(result, status=status.HTTP_200_OK, content_type="application/json")
            response.__setitem__(header="HTTP_AUTHORIZATION", value=token)
            return response
        except User.DoesNotExist as e:
            result = {'status': False, 'message': 'User does not exist'}
            return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except AuthenticationFailed as e:
            result = {'status': False, 'message': 'Invalid credentials'}
            return Response(result, status.HTTP_401_UNAUTHORIZED, content_type="application/json")
        except Exception as e:
            result = {'status': False, 'message': 'Some other issue.Please try again'}
            return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")

    @method_decorator(user_login_required, name='dispatch')
    def get(self, request, **kwargs):
        """[deletes current user's token from cache]

        :param kwargs: [mandatory]:[string]authentication token containing user id
        :return:log out confirmation and status code
        """
        try:
            cache = Cache.getInstance()
            current_user = kwargs['userid']
            if cache.get("TOKEN_" + str(current_user) + "_AUTH"):
                cache.delete("TOKEN_" + str(current_user) + "_AUTH")

            result={'status':True, 'message':'Logged out'}

            return Response(result, status=status.HTTP_200_OK, content_type="application/json")
        except Exception as e:
            result = {'status': True, 'message': 'some other issue.Please try again'}
            return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")








#TODO:url-> 1.send reset email 2.url slugfield(as arg) connected with another view
class RequestPasswordResetEmail(APIView):
    """[sends an email to facilitate password reset]
    """
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request,**kwargs):
        """[sends an email to facilitate password reset]

        :param request: [mandatory]:[string]:email of user
        :return: [string] confirmation message
                 email with link to reset password
                 [int] status code
        """
        try:
            email = request.data.get('email', '')

            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)
                #redirect_url = request.build_absolute_uri(reverse("password-reset-complete"))
                redirect_url = 'http://127.0.0.1:8000/users/reset-password-complete/' #TODO:try to user reverse

                email_body = 'Hello, \n Your token number is : ' + token + ' \n your uidb64 code is ' + uidb64 + ' \n Use link below to reset your password  \n' + "?redirect_url=" + redirect_url
                data = {'email_body': email_body, 'to_email': user.email,'email_subject': 'Reset your passsword'}
                Util.send_reset_email(data)
                result = {'status':True ,'message':'We have sent you a link to reset your password' }
                return Response(result, status=status.HTTP_200_OK, content_type="application/json")

            else:
                result = {'status': False, 'message': "Email id you have entered doesn't exist"}
                return Response(result, status=status.HTTP_400_BAD_REQUEST, content_type="application/json")


        except Exception as e:
            result = {'status': False, 'message': 'Something went wrong.Please try again.'}
            return Response(result, status=status.HTTP_400_BAD_REQUEST, content_type="application/json")


class SetNewPassword(APIView):
    """[returns new password when supplied with uid,token and new password]
    """
    serializer_class = SetNewPasswordSerializer

    def patch(self, request,**kwargs):
        """[returns new password when supplied with uid,token and new password]

        :param request: [mandatory]:[string]: new password
        :return: confirmation message and status code
        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = {'status': True, 'message': 'Password reset successful'}
        return Response(result, status=status.HTTP_200_OK, content_type="application/json")


