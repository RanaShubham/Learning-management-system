import datetime
from .serializers import LoginSerializer,RegisterSerializer
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
        """[To get all the registered account details when logged in as admin.]

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
        """[create account for user by taking in user details]

        :param kwargs: [mandatory]:[string]dictionary containing requesting user's id generated from decoded token
        :param request:[mandatory]: name,email,role,phone_number of user to be created
        :return:creation confirmation and status code.Email is sent to host email account.
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
            return Response(result, status.HTTP_404_NOT_FOUND, content_type="application/json")
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
            result = {'status': False, 'message': 'Account does not exist'}
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













