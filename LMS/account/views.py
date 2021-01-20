from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .dummy_data import get_response

# Create your views here.
class GetUser(APIView):
    def get(self , request, **kwargs):
        return Response({'status':True, "message":get_response}, status=status.HTTP_200_OK)

class RegisterUser(APIView):
    def post(self, request, **kwargs):
        #TODO: ADD USER IN DB HERE.
        response = {'status':True,'message':'Created successfully'}
        return Response(response, status=status.HTTP_201_CREATED)

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