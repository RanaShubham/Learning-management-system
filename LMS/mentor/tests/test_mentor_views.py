from django.urls import reverse
from rest_framework import status
import pytest,json
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from LMS.utils import LMSException, ExceptionType
from services.cache import Cache

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
        self.login_url = reverse("account:login_user")
        self.mentor_login_url = reverse("account:login_user")
        self.post_role_url = reverse("account:post_role")
        self.post_course_url = reverse("course-register")
        self.get_mentors_url = reverse("mentor:get_mentors")
        self.post_mentor_url = reverse("mentor:post_mentor")
        self.get_delete_mentor_url = reverse("mentor:get_delete_mentor",kwargs={'pk':'2'} )
        self.invalid_get_delete_mentor_url = reverse("mentor:get_delete_mentor", kwargs={'pk': '1'})

        self.admin_data = {'email': "admin@email.com",
                           'password': "adminpass"}
        self.mentor_data = {'email': "mentorZ@gmail.com",
                           'password':""}

        self.role_data = {'role_id':2,
            'role':"mentor"
        }

        self.valid_mentor_registration_data = {'name': "mentorZ",
                                        'role': "mentor",
                                        'email': "mentorZ@gmail.com",
                                        'phone_number': '123456789'
                                        }
        self.course_data = {'name':"Python",
                                  'price':3456.78,
                                  'duration':"3 months",
                                  'description':"Python for beginners"
                                 }
        self.valid_mentor_data = {'user': "mentorZ@gmail.com",
                                    'course': "Python"}
        self.invalid_mentor_data = {'user': "mentorZ@gmail.com",
                                  'course': "Java"}

    def test_admin_get_all_users(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.get(self.get_mentors_url, HTTP_AUTHORIZATION = Authorization,format='json' )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_post_delete_mentor(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.post(self.post_role_url, self.role_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.post_course_url, self.course_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.register_url, self.valid_mentor_registration_data,HTTP_AUTHORIZATION=Authorization,format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.post_mentor_url, self.valid_mentor_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(self.get_delete_mentor_url, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.get_delete_mentor_url, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_post_mentor_for_non_existent_mentor_returns_404_NOT_FOUND(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Authorization = response.get('HTTP_AUTHORIZATION')

        response = self.client.post(self.post_mentor_url, self.valid_mentor_data, HTTP_AUTHORIZATION=Authorization,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_invalid_course_field_in_mentor_data_returns_404_NOT_FOUND(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.post(self.post_role_url, self.role_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.post_course_url, self.course_data, HTTP_AUTHORIZATION=Authorization,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.register_url, self.valid_mentor_registration_data,
                                    HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.post_mentor_url, self.invalid_mentor_data, HTTP_AUTHORIZATION=Authorization,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_get_id_returns_404_NOT_FOUND(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Authorization = response.get('HTTP_AUTHORIZATION')

        response = self.client.get(self.get_delete_mentor_url, HTTP_AUTHORIZATION=Authorization,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_delete_id_returns_404_NOT_FOUND(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.get(self.get_delete_mentor_url, HTTP_AUTHORIZATION=Authorization,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_with_mentor_credentials_post_new_mentor_should_return_401_UNAUTHORIZED(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        self.client.post(self.post_role_url, self.role_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.post_course_url, self.course_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.register_url, self.valid_mentor_registration_data,HTTP_AUTHORIZATION=Authorization,format='json')
        self.client.post(self.post_mentor_url, self.valid_mentor_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.mentor_data['password']= Cache.getInstance().get("TOKEN_password_AUTH").decode('utf-8')
        response = self.client.post(self.mentor_login_url, self.mentor_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        response=self.client.post(self.post_mentor_url, self.valid_mentor_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_post_existing_mentor_data_should_return_400_BAD_REQUEST(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        self.client.post(self.post_role_url, self.role_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.post_course_url, self.course_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.register_url, self.valid_mentor_registration_data, HTTP_AUTHORIZATION=Authorization,
                         format='json')
        response=self.client.post(self.post_mentor_url, self.valid_mentor_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response=self.client.post(self.post_mentor_url, self.valid_mentor_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_with_mentor_credentials_get_all_or_specific_mentor_should_return_401_UNAUTHORIZED(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        self.client.post(self.post_role_url, self.role_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.post_course_url, self.course_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.register_url, self.valid_mentor_registration_data,HTTP_AUTHORIZATION=Authorization,format='json')
        self.client.post(self.post_mentor_url, self.valid_mentor_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.mentor_data['password']= Cache.getInstance().get("TOKEN_password_AUTH").decode('utf-8')
        response = self.client.post(self.mentor_login_url, self.mentor_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.get(self.get_mentors_url, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.get(self.invalid_get_delete_mentor_url, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_delete_with_wrong_id_should_return_404_NOT_FOUND(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.delete(self.get_delete_mentor_url, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_delete_with_mentor_credentials_should_return_401_UNAUTHORIZED(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        self.client.post(self.post_role_url, self.role_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.post_course_url, self.course_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.register_url, self.valid_mentor_registration_data, HTTP_AUTHORIZATION=Authorization,
                         format='json')
        self.client.post(self.post_mentor_url, self.valid_mentor_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.mentor_data['password'] = Cache.getInstance().get("TOKEN_password_AUTH").decode('utf-8')
        response = self.client.post(self.mentor_login_url, self.mentor_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.delete(self.get_delete_mentor_url, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
