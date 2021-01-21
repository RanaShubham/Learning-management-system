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













#
# from django.shortcuts import render
# from rest_framework.exceptions import AuthenticationFailed
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .dummy_data import get_response
# from .utils import Util
# from .serializers import RegisterSerializer,LoginSerializer
# from .models import *
# from rest_framework import serializers
#
# import datetime
# # from .models import UserManager
#
# # Create your views here.
# class GetUser(APIView):
#     def get(self , request, **kwargs):
#         user=User.objects.filter(email='admin6@gmail.com').first()
#         return Response({'status':True, "message":user}, status=status.HTTP_200_OK)
#
# class RegisterUser(APIView):
#     serializer_class = RegisterSerializer
#     def post(self, request, **kwargs):
#         #TODO: ADD USER IN DB HERE.
#
#         """
#         create account for user by taking in user details
#
#         Args:
#             request ([type]): [description]
#
#         Returns:
#             Response (json): json data if credentials are matched
#         """
#         # print(request.data)
#         # request.POST._mutable = True
#         # request.data['password']=get_random_password()
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         user_data = serializer.data
#         # password2 = get_random_password()
#         # print(get_random_password())
#         # print(password2)
#         user = User.objects.get(email=user_data['email'], name=user_data['name'], phone_number=user_data['phone_number'], role=user_data['role'])
#         print(user)
#         Util.send_email(user)
#         response = {'status':True,'message':'Registered successfully. Login Crdentials have been sent to your email.'}
#         return Response(response, status=status.HTTP_200_OK)
#
# class UpdateUser(APIView):
#     def patch(self, request, **kwargs):
#         #TODO: Update USER IN DB HERE.
#         response = {'status':True,'message':'Updated successfully'}
#         return Response(response, status=status.HTTP_200_OK)
#
# class LoginUser(APIView):
#
#     def post(self, request):
#         """[validates user email and password, sets user id in cache]
#
#         :param request:[mandatory]:[string]:email of user
#                                    [string]:password
#         :return: [dictionary]:status[boolean]
#                               response message[string]
#                               token[string]
#                  [int]:status code
#         """
#         try:
#             serializer = LoginSerializer(data=request.data)
#             print('serialized')
#             serializer.is_valid(raise_exception=True)
#             print(serializer.errors)
#             data=serializer.data
#             print(data)
#             user = User.objects.filter(email=data['email']).first()
#             print(user)
#             current_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
#             #token = Encrypt.encode(user.id,current_time)
#             #cache.set("TOKEN_"+str(user.id)+"_AUTH", token)
#             #result = utils.manage_response(status=True, message='Token generated', log='successfully logged in', logger_obj=logger)
#             result = {'status':True,'message':' Login successful.'}
#             response = Response(result, status=status.HTTP_200_OK,content_type="application/json")
#             #response.__setitem__(header="HTTP_AUTHORIZATION",value=token)
#             return response
#
#         except serializers.ValidationError as se:
#             #logging.warning(se)
#             response = {'message':str(se.detail), 'status':False}
#             return Response(response, status=status.HTTP_400_BAD_REQUEST)
#
#         except User.DoesNotExist as e:
#             result = {'status':False,'message':str(e)}
#             return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")
#         except AuthenticationFailed as e:
#             result ={'status':False,'message':str(e)}
#
#             return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")
#         except Exception as e:
#             result = {'status':False,'message':str(e)}
#             return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")