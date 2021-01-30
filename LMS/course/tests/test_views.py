from django.urls import reverse
from rest_framework import status
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


User = get_user_model()

client = APIClient()


@pytest.mark.django_db()
class Data(TestCase):
    """
    this class will initialise all the urls and data and it is inherited by other test classes
    """

    def setUp(self):
        """
        this method setup all the url and data which was required by all test cases
        """
        self.admin_login_url = reverse("account:login_user")
        self.course_register_url = reverse("course-register")
        self.single_course_url = reverse("specific-course", kwargs={"pk": 1})

        self.admin_login_data = {
            'email': 'adminpass@gmail.com',
            'password': 'adminpassword'
        }

        self.valid_course_details = {
            "name": "Python",
            "price": "7500",
            "duration": "4 months",
            "description": "Very simple but challenging",
        }
        self.valid_patch_data = {
            "price": "9517"
        }
        self.invalid_course_details = {
            "name": "maven",
            "duration": "6 months",
        }
        user = User.objects.create_superuser(name='admin', email='adminpass@gmail.com', phone_number='1234',
                                             password='adminpassword')


class CourseDetailsTest(Data):

    def test_course_with_valid_details(self):
        response = self.client.post(self.admin_login_url, self.admin_login_data, format='application/json')
        headers = response.__getitem__(header="HTTP_AUTHORIZATION")
        response = self.client.post(self.course_register_url, self.valid_course_details, HTTP_AUTHORIZATION=headers,
                                    format='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.single_course_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.single_course_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.course_register_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = client.patch(self.single_course_url, self.valid_patch_data, HTTP_AUTHORIZATION=headers,
                                format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = client.delete(self.single_course_url, HTTP_AUTHORIZATION=headers,
                                format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_course_with_invalid_details(self):
        response = self.client.post(self.admin_login_url, self.admin_login_data, format='application/json')
        headers = response.__getitem__(header="HTTP_AUTHORIZATION")
        response = self.client.post(self.course_register_url, self.invalid_course_details, HTTP_AUTHORIZATION=headers,
                                    format='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
