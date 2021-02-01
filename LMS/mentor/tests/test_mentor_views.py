from django.urls import reverse
from rest_framework import status
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

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
        self.post_role_url = reverse("account:get_post_role")
        self.post_course_url = reverse("course-register")
        self.get_mentors_url = reverse("mentor:get_mentors")
        self.post_mentor_url = reverse("mentor:post_mentor")
        self.get_delete_mentor_url = reverse("mentor:get_update_delete_mentor",kwargs={'pk':'2'} )
        self.invalid_get_delete_mentor_url = reverse("mentor:get_update_delete_mentor", kwargs={'pk': '1'})

        self.admin_data = {'email': "admin@email.com",
                           'password': "adminpass"}
        self.mentor_data = {'email': "mentorZ@gmail.com",
                           'password':""}

        self.role_data = {'role_id':2,
                          'role':"mentor"
                         }
        self.valid_patch_data = {'course': [1,2]}
        self.invalid_user_patch_data = {'user':3}
        self.invalid_course_patch_data = {'course': [3]}


        self.course_data = {'name':"Python",
                            'price':3456.78,
                            'duration':"3 months",
                            'description':"Python for beginners"
                           }
        self.course_data2 = {'name': "Java",
                            'price': 3456.78,
                            'duration': "3 months",
                            'description': "Java for beginners"
                            }

        self.valid_mentor_data = {'name': "mentorZ",
                                  'role': "mentor",
                                  'email': "mentorZ@gmail.com",
                                  'phone_number': '123456789',
                                  'course': [1]}

        self.invalid_mentor_data = {'name': "mentorZ",
                                  'role': "mentor",
                                  'email': "mentorZ@gmail.com",
                                  'phone_number': '123456789',
                                    'course': [4]}
        self.invalid_role_mentor_data = {'name': "mentorZ",
                                    'role': "student",
                                    'email': "mentorZ@gmail.com",
                                    'phone_number': '123456789',
                                    'course': [1]}


    def test_admin_get_all_users(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.get(self.get_mentors_url, HTTP_AUTHORIZATION = Authorization,format='json' )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_get_post_delete_mentor(self):
        client=APIClient()
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.post(self.post_role_url, self.role_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.post(self.post_course_url, self.course_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.post_course_url, self.course_data2, HTTP_AUTHORIZATION=Authorization,format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.post_mentor_url, self.valid_mentor_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = client.patch(self.get_delete_mentor_url, self.valid_patch_data, HTTP_AUTHORIZATION=Authorization,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.get_delete_mentor_url, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.get_delete_mentor_url, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_get_id_returns_404_NOT_FOUND(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.get(self.get_delete_mentor_url, HTTP_AUTHORIZATION=Authorization,format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_get_all_or_specific_mentor_with_mentor_credentials_should_return_401_UNAUTHORIZED(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        self.client.post(self.post_role_url, self.role_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.post_course_url, self.course_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.post_mentor_url, self.valid_mentor_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.mentor_data['password']= Cache.getInstance().get("TOKEN_password_AUTH").decode('utf-8')
        response = self.client.post(self.mentor_login_url, self.mentor_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.get(self.get_mentors_url, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.get(self.invalid_get_delete_mentor_url, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_invalid_course_field_in_mentor_data_returns_404_NOT_FOUND(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        self.client.post(self.post_role_url, self.role_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.post_course_url, self.course_data, HTTP_AUTHORIZATION=Authorization,format='json')
        response = self.client.post(self.post_mentor_url, self.invalid_mentor_data, HTTP_AUTHORIZATION=Authorization,format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_post_new_mentor_with_mentor_credentials_should_return_401_UNAUTHORIZED(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        self.client.post(self.post_role_url, self.role_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.post_course_url, self.course_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.post_mentor_url, self.valid_mentor_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.mentor_data['password']= Cache.getInstance().get("TOKEN_password_AUTH").decode('utf-8')
        response = self.client.post(self.mentor_login_url, self.mentor_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        response=self.client.post(self.post_mentor_url, self.valid_mentor_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_post_wrong_role_name_returns_400_BAD_REQUEST(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        self.client.post(self.post_role_url, self.role_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.post_course_url, self.course_data, HTTP_AUTHORIZATION=Authorization, format='json')
        response = self.client.post(self.post_mentor_url, self.invalid_role_mentor_data, HTTP_AUTHORIZATION=Authorization,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_post_existing_mentor_data_should_return_400_BAD_REQUEST(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        self.client.post(self.post_role_url, self.role_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.post_course_url, self.course_data, HTTP_AUTHORIZATION=Authorization, format='json')
        response=self.client.post(self.post_mentor_url, self.valid_mentor_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response=self.client.post(self.post_mentor_url, self.valid_mentor_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
        self.client.post(self.post_mentor_url, self.valid_mentor_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.mentor_data['password'] = Cache.getInstance().get("TOKEN_password_AUTH").decode('utf-8')
        response = self.client.post(self.mentor_login_url, self.mentor_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.delete(self.get_delete_mentor_url, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_delete_id_returns_404_NOT_FOUND(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.get(self.get_delete_mentor_url, HTTP_AUTHORIZATION=Authorization,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_patch_with_mentor_credentials_should_return_401_UNAUTHORIZED(self):
        client = APIClient()
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        self.client.post(self.post_role_url, self.role_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.post_course_url, self.course_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.post_mentor_url, self.valid_mentor_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.mentor_data['password'] = Cache.getInstance().get("TOKEN_password_AUTH").decode('utf-8')
        response = self.client.post(self.mentor_login_url, self.mentor_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = client.patch(self.get_delete_mentor_url, self.valid_patch_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_patch_for_non_existent_mentor_should_return_404_NOT_FOUND(self):
        client = APIClient()
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = client.patch(self.invalid_get_delete_mentor_url, self.valid_patch_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_patch_for_user_id_should_return_401_UNAUTHORIZED(self):
        client = APIClient()
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.post(self.post_role_url, self.role_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.post(self.post_course_url, self.course_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.post_course_url, self.course_data2, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.post(self.post_mentor_url, self.valid_mentor_data, HTTP_AUTHORIZATION=Authorization,
                                    format='json')
        response = client.patch(self.get_delete_mentor_url, self.invalid_user_patch_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_patch_for_course_should_return_404_NOT_FOUND(self):
        client = APIClient()
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.post(self.post_role_url, self.role_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.post(self.post_course_url, self.course_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.post_course_url, self.course_data2, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.post(self.post_mentor_url, self.valid_mentor_data, HTTP_AUTHORIZATION=Authorization,
                                    format='json')
        response = client.patch(self.get_delete_mentor_url, self.invalid_course_patch_data,HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)