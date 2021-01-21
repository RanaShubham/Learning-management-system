from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .dummy_data import get_response
from .utils import Util
from .serializers import RegisterSerializer
from .models import *
# from .models import UserManager

# Create your views here.
class GetUser(APIView):
    def get(self , request, **kwargs):
        return Response({'status':True, "message":get_response}, status=status.HTTP_200_OK)

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
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'], name=user_data['name'], phone_number=user_data['phone_number'], role=user_data['role'])
        # print("aaya")
        Util.send_email(user)
        response = {'status':True,'message':'Registered successfully. Login Crdentials have been sent to your email.'}
        return Response(response, status=status.HTTP_200_OK)

class UpdateUser(APIView):
    def patch(self, request, **kwargs):
        #TODO: Update USER IN DB HERE.
        response = {'status':True,'message':'Updated successfully'}
        return Response(response, status=status.HTTP_200_OK)

class LoginUser(APIView):
    def post(self, request, *args, **kwargs):
        #TODO: LOGIN USER HERE.
        response = {'status':True,'message':'Logged in successfully'}
        return Response(response, status=status.HTTP_200_OK)