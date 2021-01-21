from django.shortcuts import render
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .dummy_data import get_response
from .utils import Util
from .serializers import RegisterSerializer,LoginSerializer
from .models import *
from rest_framework import serializers

import datetime
# from .models import UserManager

# Create your views here.
class GetUser(APIView):
    def get(self , request, **kwargs):
        user=User.objects.filter(email='asdfgh@gmail.com').first()
        return Response({'status':True, "message":user}, status=status.HTTP_200_OK)

class RegisterUser(APIView):
    serializer_class = RegisterSerializer
    def post(self, request, **kwargs):
        #TODO: ADD USER IN DB HERE.
        
        """
        create account for user by taking in user details

        Args:
            request ([type]): [description]

        Returns:
            Response (json): json data if credentials are matched
        """
        # print(request.data)
        # request.POST._mutable = True
        # request.data['password']=get_random_password()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        # password2 = get_random_password()
        # print(get_random_password())
        # print(password2)
        user = User.objects.get(email=user_data['email'], name=user_data['name'], phone_number=user_data['phone_number'], role=user_data['role'])
        print(user)
        Util.send_email(user)
        response = {'status':True,'message':'Registered successfully. Login Crdentials have been sent to your email.'}
        return Response(response, status=status.HTTP_200_OK)

class UpdateUser(APIView):
    def patch(self, request, **kwargs):
        #TODO: Update USER IN DB HERE.
        response = {'status':True,'message':'Updated successfully'}
        return Response(response, status=status.HTTP_200_OK)

class LoginUser(APIView):

    def post(self, request):
        """[validates user email and password, sets user id in cache]

        :param request:[mandatory]:[string]:email of user
                                   [string]:password
        :return: [dictionary]:status[boolean]
                              response message[string]
                              token[string]
                 [int]:status code
        """
        try:
            serializer = LoginSerializer(data=request.data)
            print('serialized')
            serializer.is_valid(raise_exception=True)
            print(serializer.errors)
            data=serializer.data
            print(data)
            user = User.objects.filter(email=data['email']).first()
            print(user)
            current_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            #token = Encrypt.encode(user.id,current_time)
            #cache.set("TOKEN_"+str(user.id)+"_AUTH", token)
            #result = utils.manage_response(status=True, message='Token generated', log='successfully logged in', logger_obj=logger)
            result = {'status':True,'message':' Login successful.'}
            response = Response(result, status=status.HTTP_200_OK,content_type="application/json")
            #response.__setitem__(header="HTTP_AUTHORIZATION",value=token)
            return response

        except serializers.ValidationError as se:
            #logging.warning(se)
            response = {'message':str(se.detail), 'status':False}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist as e:
            result = {'status':False,'message':str(e)}
            return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")
        except AuthenticationFailed as e:
            result ={'status':False,'message':str(e)}

            return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except Exception as e:
            result = {'status':False,'message':str(e)}
            return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")