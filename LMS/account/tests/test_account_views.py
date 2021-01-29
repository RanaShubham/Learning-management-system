from django.urls import reverse
from rest_framework import status
import pytest,json
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from LMS.utils import LMSException, ExceptionType

User = get_user_model()


@pytest.mark.django_db
class Data(TestCase):
    """
    initialises all the urls and data 
    """    

    def setUp(self):
        """
        this method setup all the url and data which was required by all test cases
        """
        User.objects.create_superuser(name="admin", email="admin@email.com", phone_number="1234567890", password="adminpass")


        self.register_url = reverse("account:post_user")
        self.get_url = reverse("account:get_users")
        self.login_url = reverse("account:login_user")
        self.logout_url = reverse("account:logout_user")
        self.patch_url = reverse("account:update_delete_user", kwargs={'pk':'1'})
        self.admin_data = {'email': "admin@email.com", 'password': "adminpass"}


        self.valid_registration_data = {'name': "adam",
                                        'role': "admin",
                                        'email': "adam@gmail.com",
                                        'phone_number': '123456789'
                                        }
        self.invalid_login_data_invalid_credentials = {
            'email' : "adam@gmail.com",
            'password': 'password'
        }
        self.invalid_register_data ={
            'name': "adam",
            'role': "principal",
            'email': "adam@gmail.com",
            'phone_number': '123456789'
        }
        self.valid_patch_data ={
            'phone_number': '95236'
        }

    def test_login_admin(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_admin(self):
        response=self.client.post(self.login_url, self.admin_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.get(self.logout_url, HTTP_AUTHORIZATION = Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_register_demo(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization= response.get('HTTP_AUTHORIZATION')
        response = self.client.post(self.register_url, self.valid_registration_data, HTTP_AUTHORIZATION = Authorization,format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_demo(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization= response.get('HTTP_AUTHORIZATION')
        response = self.client.get(self.get_url, HTTP_AUTHORIZATION = Authorization,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_demo(self):
        client = APIClient()
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization= response.get('HTTP_AUTHORIZATION')
        response = client.patch(self.patch_url, self.valid_patch_data, HTTP_AUTHORIZATION = Authorization,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization= response.get('HTTP_AUTHORIZATION')
        self.client.post(self.register_url, self.valid_registration_data, HTTP_AUTHORIZATION=Authorization,
                                    format='json')
        response = self.client.delete(self.patch_url,HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_login_admin_returns_401_UNAUTHORIZED(self):
        response = self.client.post(self.login_url, self.invalid_login_data_invalid_credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) 

    def test_invalid_register_returns_400_BAD_REQUEST(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization= response.get('HTTP_AUTHORIZATION')
        response = self.client.post(self.register_url, self.invalid_register_data, HTTP_AUTHORIZATION = Authorization, format='json')#HTTP_AUTHORIZATION = Authorization
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_get_returns_400_BAD_REQUEST(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.get_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_patch_(self):
        client = APIClient()
        response = client.patch(self.patch_url, self.valid_patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_token_returns_400_BAD_REQUEST(self):  # DECODE ERROR
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization = response.get('HTTP_AUTHORIZATION').replace("m","M")
        response = self.client.get(self.get_url, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

