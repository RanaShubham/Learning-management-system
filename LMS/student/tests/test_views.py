from django.http import HttpResponse
from django.urls import reverse
from rest_framework import status
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from account.models import Role
from services.cache import Cache

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
        self.admin_register_user = reverse("account:post_user")
        self.student_register_url = reverse("student-register")
        self.single_student_url = reverse("student-details", kwargs={"pk": 2})

        self.admin_login_data = {
            'email': 'adminpass@gmail.com',
            'password': 'adminpassword'
        }

        self.admin_register_user_data = {
            'email': 'random_email@gmail.com',
            'name': 'random',
            'phone_number': '92345',
            'role': 'student',
        }
        self.student_login_data = {
            'email': 'random_email@gmail.com',
        }
        self.valid_student_form = {
            "alternate_contact_number": "9517538",
            "relationship_of_alternate_contact_person": "Parent",
            "current_location": "Delhi",
            "current_address": "170, Ber Sarai, Hauz Khas, Delhi",
            "git_link": "github.com/astroboy",
            "college_name": "IIIT Bhubaneswar",
            "university": "IIIT Bhubaneswar",
            "degree": "B.Tech",
            "degree_stream": "CS",
            "degree_percentage": 70,
            "degree_graduation_year": 2019,
            "masters_stream": "AI",
            "masters_percentage": 77,
            "year_of_job_experience": 1,
            "year_of_masters": 2023,
            "masters": "Mtech"
        }
        self.valid_patch_data = {
            "alternate_contact_number": "9517"
        }
        self.invalid_student_form = {
            "alternate_contact_number": "9517538",
            "relationship_of_alternate_contact_person": "Parent",
        }
        user = User.objects.create_superuser(name='admin', email='adminpass@gmail.com', phone_number='1234',
                                             password='adminpassword')

        role = Role.objects.create(role_id=2, role='student')

        response = self.client.post(self.admin_login_url, self.admin_login_data, format='application/json')
        headers = response.__getitem__(header="HTTP_AUTHORIZATION")
        self.client.post(self.admin_register_user, self.admin_register_user_data, HTTP_AUTHORIZATION=headers,
                         format='application/json ')
        password = Cache.getInstance().get("TOKEN_" + "password" + "_AUTH").decode("utf-8")
        self.student_login_data['password'] = password


class StudentDetailsTest(Data):

    def test_student_with_valid_details(self):

        response = self.client.post(self.admin_login_url, self.student_login_data, format='application/json')
        headers = response.__getitem__(header="HTTP_AUTHORIZATION")
        response = self.client.post(self.student_register_url, self.valid_student_form, HTTP_AUTHORIZATION=headers,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.single_student_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.patch(self.single_student_url, self.valid_patch_data, HTTP_AUTHORIZATION=headers,
                                format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_with_invalid_details(self):
        response = self.client.post(self.admin_login_url, self.student_login_data, format='application/json')
        headers = response.__getitem__(header="HTTP_AUTHORIZATION")
        response = self.client.post(self.student_register_url, self.invalid_student_form, HTTP_AUTHORIZATION=headers,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
