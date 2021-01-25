import datetime
from django.urls import reverse
from django.utils.encoding import force_str
import jwt
from .serializers import LoginSerializer,RegisterSerializer,ResetPasswordEmailRequestSerializer,SetNewPasswordSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from .decorators import user_login_required
from .models import Role, User
from services.encrypt import Encrypt
from services.cache import Cache
from .utils import Util
from rest_framework import serializers
from LMS.utils import ExceptionType, LMSException

admin_role_id = Role.objects.get(role='admin').role_id

@method_decorator(user_login_required, name='dispatch')
class RegisterUser(APIView):

    def get(self, request,**kwargs):
        """[To get all the registered User details when logged in as admin.]

        :param kwargs: [mandatory]:[string]dictionary containing requesting user's
         id generated from decoded token
        :return:Response with status of success and data if successful.
        """
        try:
            current_user_id = kwargs.get('userid')
            if User.objects.get(id=current_user_id).role.role_id != admin_role_id:
                raise LMSException(ExceptionType.UnauthorizedError,"You are not authorized to perform this operation.")

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
        except Exception as e:
            response = {'status':False, 'message':'Somethign went wrong.'}
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, **kwargs):
        """[create User for user by taking in user details]

        :param kwargs: [mandatory]:[string]dictionary containing requesting user's id
         generated from decoded token
        :param request:[mandatory]: name,email,role,phone_number of user to be created
        :return:creation confirmation and status code.Email is sent to host email User.
        """
        try:
            requesting_user_id = kwargs.get('userid')
            requesting_user_role = User.objects.get(id=requesting_user_id).role
            # requesting_user_role_name = Role.objects.get(role_id =  requesting_user_role_id).role_name
            if requesting_user_role.role_id != admin_role_id:
                raise LMSException(ExceptionType.UnauthorizedError,"You are not authorized to perform this operation.")

            normalized_admission_role = request.data['role'].lower()
            
            admission_role_obj = Role.objects.filter(role = normalized_admission_role).first()

            if not admission_role_obj:
                raise LMSException(ExceptionType.RoleError, "{} is not a valid role.".format(normalized_admission_role))

            request.POST._mutable = True
            request.data['role'] = admission_role_obj.pk
            request.POST._mutable = False

            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            user = User.objects.get(email=request.data.get('email'))
            Util.send_email(user)
            response = {'status': True,
                        'message': 'Registered successfully. Login Credentials have been sent to your email.'}
            return Response(response, status=status.HTTP_200_OK)

        except KeyError as e:
            result = {'status': False, 'message':"Please specify a role for the user to be registered."}
            return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except LMSException as e:
            result = {'status':False, 'message':e.message}
            return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except serializers.ValidationError as e:
            result = {'status': False, 'message': e.detail}
            return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except Exception as e:
            result = {'status': False, 'message': str(e)}
            return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")



    def patch(self,request,pk,**kwargs):
        """[updates a user's one or more credentials]

        :param kwargs: [mandatory]:[string]dictionary containing requesting user's id generated from decoded token
        :return:updation confirmation, new details and status code
        """

        try:
            current_user_id = kwargs.get('userid')
            if  User.objects.get(id=current_user_id).role.role_id != admin_role_id:
                raise LMSException(ExceptionType.UnauthorizedError,"You are not authorized to perform this operation.")

            if not User.objects.filter(id=pk).exclude(is_deleted=True).exists():
                raise LMSException(ExceptionType.NonExistentError, "No updatable record found.")
            user = User.objects.get(id=pk)
            #If update contains 'role' update.
            if request.data.get('role'):
                normalized_admission_role = request.data.get('role').lower()
                admission_role_obj = Role.objects.filter(role = normalized_admission_role).first()
                request.POST._mutable = True
                request.data['role'] = admission_role_obj.pk
                request.POST._mutable = False

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
            if User.objects.get(id=current_user_id).role.role_id != admin_role_id:
                raise LMSException(ExceptionType.UnauthorizedError, "You are not authorized to perform this operation.")

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
            result = {'status': False, 'message': str(e)}
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
                current_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                token = force_str(Encrypt.encode(user.id, current_time))
                Cache.getInstance().set("RESET_" + str(user.id) + "_TOKEN", token)
                redirect_url = reverse('account:reset_password', kwargs={'reset_token':token})
                email_body = 'Hello, please click on the link below and enter new password when asked for\n'+redirect_url
                data = {'email_body': email_body, 'to_email': user.email,'email_subject': 'Reset your passsword'}
                Util.send_reset_email(data)
                result = {'status':True ,'message':'We have sent you a link to reset your password' }
                return Response(result, status=status.HTTP_200_OK, content_type="application/json")
            else:
                result = {'status': False, 'message': "Email id you have entered doesn't exist"}
                return Response(result, status=status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except Exception as e:
            result = {'status': False, 'message': str(e)}
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
        try:
            password = request.data.get('password')
            token = kwargs.get('reset_token')
            id = Encrypt.decode(token).get('id')
            cached_reset_token = force_str(Cache.getInstance().get("RESET_" + str(id) + "_TOKEN"))
            if cached_reset_token == 'None':
                raise LMSException(ExceptionType.UnauthorizedError, "reset password url is expired.")

            if cached_reset_token != token:
                raise LMSException(ExceptionType.UnauthorizedError, "reset password url is invalid.")
            
            if not password or len(password) <= 2:
                raise LMSException(ExceptionType.UserException,\
                     "Please provide a appropirate password with atleast 3 character.")

            user = User.objects.get(id=id)
            user.set_password(password)
            user.save()
            Cache.getInstance().delete("RESET_" + str(id) + "_TOKEN")
            result = {'status': True, 'message': 'Password reset successful'}
            return Response(result, status=status.HTTP_200_OK, content_type="application/json")
        except jwt.exceptions.InvalidSignatureError as e:
            result = {'status':False, 'message':"reset password url is corrupt."}
            return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except LMSException as e:
            result = {'status':False, 'message':e.message}
            return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except Exception as e:
            return Response({'message':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type="application/json")


