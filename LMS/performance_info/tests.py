from django.test import TestCase
from django.urls import reverse
from rest_framework import status
import pytest,json
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from LMS.utils import LMSException, ExceptionType

# Create your tests here.
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

    def test_demo:
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
