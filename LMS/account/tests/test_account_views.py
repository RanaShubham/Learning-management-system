from django.urls import reverse
from rest_framework import status
import pytest,json
from django.test import TestCase
from django.contrib.auth import get_user_model
from account.utils import store
from rest_framework.test import APIClient

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
        client = APIClient()
        User.objects.create_superuser(name="admin", email="admin@email.com", phone_number="1234567890", password="adminpass")
        self.register_url = reverse("account:register_get_update_delete", kwargs={'pk':''})
        self.login_url = reverse("account:login_user")
        self.patch_url = reverse("account:register_get_update_delete", kwargs={'pk':'1'})
        password = ''.join(store())
        self.admin_data = {'email': "admin@email.com", 'password': "adminpass"}
        self.valid_registration_data = {'name': "adam",
                                        'role': "admin",
                                        'email': "adam@gmail.com",
                                        'phone_number': '123456789'
                                        }
        self.valid_login_data = {
            'email' : "adam@gmail.com",
            'password': password
        }
        self.valid_patch_data ={
            'phone_number': '95236'
        }

    def test_login_admin(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
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
        response = self.client.get(self.register_url, HTTP_AUTHORIZATION = Authorization,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_patch_demo(self):
        client = APIClient()
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization= response.get('HTTP_AUTHORIZATION')
        response = client.patch(self.patch_url, self.valid_patch_data, HTTP_AUTHORIZATION = Authorization,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)   
