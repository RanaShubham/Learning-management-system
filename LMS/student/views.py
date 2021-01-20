from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .dummy_data import get_response
from rest_framework import status


class StudentDetails(APIView):

    def post(self, request):
        data = {"status": True, "message": 'student details added'}
        return Response(data, status.HTTP_201_CREATED)

    def get(self, *args, **kwargs):
        data = {"status": True, "message": 'data retrieved successfully', "data": get_response[kwargs.get("pk") - 1]}
        return Response(data, status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        get_response[kwargs.get("pk") - 1]["Name"] = "kohli"
        data = {"status": True, "message": 'data updated successfully', "data": get_response[kwargs.get("pk") - 1]}
        return Response(data, status.HTTP_200_OK)
