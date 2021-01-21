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
from LMS.utils import ExceptionType, LMSException



class RegisterUser(APIView):

    @method_decorator(user_login_required, name='dispatch')
    def get(self, request,**kwargs):
        users = User.objects.all()
        print(users)
        serializer = RegisterSerializer(users,many=True)
        response = {'status': True,
                    'message': 'Retrieved all users.','data':serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, **kwargs):
        # TODO: ADD USER IN DB HERE.

        """
        create account for user by taking in user details

        Args:
            request ([type]): [description]

        Returns:
            Response (json): json data if credentials are matched
        """
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'], name=user_data['name'],
                                phone_number=user_data['phone_number'], role=user_data['role'])
        print(user)
        Util.send_email(user)
        response = {'status': True,
                    'message': 'Registered successfully. Login Crdentials have been sent to your email.'}
        return Response(response, status=status.HTTP_200_OK)

    @method_decorator(user_login_required, name='dispatch')
    def patch(self,request,pk,**kwargs):
        if not User.objects.filter(id=pk).exists():
            raise LMSException(ExceptionType.NonExistentError, "Requested user does not exist")

        user = User.objects.get(id=pk)
        serializer = RegisterSerializer(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        user_data = serializer.data
        Util.send_email(user)
        response = {'status': True,
                    'message': 'Updated successfully.','data':user_data}
        return Response(response, status=status.HTTP_200_OK)


class LoginUser(APIView):


    def post(self, request, **kwargs):
        #TODO: Logging.
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













