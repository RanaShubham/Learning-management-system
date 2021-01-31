from django.urls import reverse
from rest_framework import status
import pytest,json
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
        self.get_url = reverse("account:get_users")
        self.get_role_url = reverse("account:get_post_role")
        self.login_url = reverse("account:login_user")
        self.logout_url = reverse("account:logout_user")
        self.post_role_url = reverse("account:get_post_role")
        self.patch_url = reverse("account:update_delete_user", kwargs={'pk':'1'})
        self.invalid_patch_url = reverse("account:update_delete_user", kwargs={'pk':'2'})
        self.reset_email_url = reverse("account:generate_reset_password_link")

        self.admin_data = {'email': "admin@email.com", 'password': "adminpass"}
        self.mentor_data = {'email': "adam@gmail.com",'password':''}
        self.email_data = {'email': "admin@email.com"}
        self.password_data = {'password': "qwerty12"}
        self.invalid_password_data = {'password': "q"}
        self.invalid_email_data = {'email': "admin1@email.com"}

        self.valid_registration_data = {'name': "adam",
                                        'role': "mentor",
                                        'email': "adam@gmail.com",
                                        'phone_number': '123456789'
                                        }
        self.invalid_registration_data1 = {'name': "qwerty",
                                        'email': "qwerty@gmail.com",
                                        'phone_number': '123456789'
                                        }
        self.invalid_registration_data2 = {
                                            'role': "admin",
                                           'email': "qwerty@gmail.com",
                                           'phone_number': '123456789'
                                           }
        self.role_data = {'role_id': 2,
                          'role': "mentor"
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
        self.invalid_patch_data = {
            'role': 'student'
        }
        self.invalid_patch_data2 = {
            'email': 'adam@gmail.com'
        }

    def test_login_admin(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_login_admin_returns_401_UNAUTHORIZED(self):
        response = self.client.post(self.login_url, self.invalid_login_data_invalid_credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_admin(self):
        response=self.client.post(self.login_url, self.admin_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.get(self.logout_url, HTTP_AUTHORIZATION = Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_register_demo(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization= response.get('HTTP_AUTHORIZATION')
        self.client.post(self.post_role_url, self.role_data, HTTP_AUTHORIZATION=Authorization, format='json')
        response = self.client.post(self.register_url, self.valid_registration_data, HTTP_AUTHORIZATION = Authorization,format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_register_returns_400_BAD_REQUEST(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.post(self.register_url, self.invalid_register_data, HTTP_AUTHORIZATION=Authorization,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_register_with_non_admin_credentials_returns_401_UNAUTHORIZED(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization1= response.get('HTTP_AUTHORIZATION')
        self.client.post(self.post_role_url, self.role_data, HTTP_AUTHORIZATION=Authorization1, format='json')
        self.client.post(self.register_url, self.valid_registration_data, HTTP_AUTHORIZATION = Authorization1, format='json')
        self.mentor_data['password'] = Cache.getInstance().get("TOKEN_password_AUTH").decode('utf-8')
        response = self.client.post(self.login_url, self.mentor_data, format='json')
        Authorization2 = response.get('HTTP_AUTHORIZATION')
        response=self.client.post(self.register_url, self.valid_registration_data, HTTP_AUTHORIZATION = Authorization2, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_register_with_no_role_returns_400_BAD_REQUEST(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization1= response.get('HTTP_AUTHORIZATION')
        response=self.client.post(self.register_url, self.invalid_registration_data1, HTTP_AUTHORIZATION = Authorization1, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_register_with_no_name_returns_400_BAD_REQUEST(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization1= response.get('HTTP_AUTHORIZATION')
        response=self.client.post(self.register_url, self.invalid_registration_data2, HTTP_AUTHORIZATION = Authorization1, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_demo(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization= response.get('HTTP_AUTHORIZATION')
        response = self.client.get(self.get_url, HTTP_AUTHORIZATION = Authorization,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_users_with_non_admin_credentials_returns_401_UNAUTHORIZED(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization= response.get('HTTP_AUTHORIZATION')
        self.client.post(self.post_role_url, self.role_data, HTTP_AUTHORIZATION=Authorization, format='json')
        self.client.post(self.register_url, self.valid_registration_data, HTTP_AUTHORIZATION = Authorization, format='json')
        self.mentor_data['password'] = Cache.getInstance().get("TOKEN_password_AUTH").decode('utf-8')
        response = self.client.post(self.login_url, self.mentor_data, format='json')
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.get(self.get_url, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_get_returns_400_BAD_REQUEST(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.get_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_get_roles(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization = response.get('HTTP_AUTHORIZATION')
        response = self.client.get(self.get_role_url, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_get_roles_with_non_admin_credentials_returns_401_UNAUTHORIZED(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization1 = response.get('HTTP_AUTHORIZATION')
        self.client.post(self.post_role_url, self.role_data, HTTP_AUTHORIZATION=Authorization1, format='json')
        self.client.post(self.register_url, self.valid_registration_data, HTTP_AUTHORIZATION=Authorization1,
                         format='json')
        self.mentor_data['password'] = Cache.getInstance().get("TOKEN_password_AUTH").decode('utf-8')
        response = self.client.post(self.login_url, self.mentor_data, format='json')
        Authorization2 = response.get('HTTP_AUTHORIZATION')
        response = self.client.get(self.get_role_url, HTTP_AUTHORIZATION=Authorization2, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_post_role_with_non_admin_credentials_returns_401_UNAUTHORIZED(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization1 = response.get('HTTP_AUTHORIZATION')
        self.client.post(self.post_role_url, self.role_data, HTTP_AUTHORIZATION=Authorization1, format='json')
        self.client.post(self.register_url, self.valid_registration_data, HTTP_AUTHORIZATION=Authorization1,
                         format='json')
        self.mentor_data['password'] = Cache.getInstance().get("TOKEN_password_AUTH").decode('utf-8')
        response = self.client.post(self.login_url, self.mentor_data, format='json')
        Authorization2 = response.get('HTTP_AUTHORIZATION')
        response = self.client.post(self.get_role_url, self.role_data,HTTP_AUTHORIZATION=Authorization2, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_demo(self):
        client = APIClient()
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization= response.get('HTTP_AUTHORIZATION')
        response = client.patch(self.patch_url, self.valid_patch_data, HTTP_AUTHORIZATION = Authorization,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_patch_with_non_existent_user_should_return_404_NOT_FOUND(self):
        client=APIClient()
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization1 = response.get('HTTP_AUTHORIZATION')
        response = client.patch(self.invalid_patch_url,self.valid_patch_data, HTTP_AUTHORIZATION=Authorization1, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_patch_trying_role_change_should_return_401_UNAUTHORIZED(self):
        client=APIClient()
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization1 = response.get('HTTP_AUTHORIZATION')
        response = client.patch(self.patch_url,self.invalid_patch_data, HTTP_AUTHORIZATION=Authorization1, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_patch_trying_email_change_should_return_400_BAD_REQUEST(self):
        client=APIClient()
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization1 = response.get('HTTP_AUTHORIZATION')
        response = client.patch(self.patch_url,self.invalid_patch_data2, HTTP_AUTHORIZATION=Authorization1, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_patch_with_non_admin_user_patch_should_return_401_UNAUTHORIZED(self):
        client=APIClient()
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization1 = response.get('HTTP_AUTHORIZATION')
        self.client.post(self.post_role_url, self.role_data, HTTP_AUTHORIZATION=Authorization1, format='json')
        self.client.post(self.register_url, self.valid_registration_data, HTTP_AUTHORIZATION=Authorization1,format='json')
        self.mentor_data['password'] = Cache.getInstance().get("TOKEN_password_AUTH").decode('utf-8')
        response = self.client.post(self.login_url, self.mentor_data, format='json')
        Authorization2 = response.get('HTTP_AUTHORIZATION')
        response = client.patch(self.patch_url,self.valid_patch_data, HTTP_AUTHORIZATION=Authorization2, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization= response.get('HTTP_AUTHORIZATION')
        self.client.post(self.register_url, self.valid_registration_data, HTTP_AUTHORIZATION=Authorization,
                                    format='json')
        response = self.client.delete(self.patch_url,HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_delete_non_admin_credentials_should_return_401_UNAUTHORIZED(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization1 = response.get('HTTP_AUTHORIZATION')
        self.client.post(self.post_role_url, self.role_data, HTTP_AUTHORIZATION=Authorization1, format='json')
        self.client.post(self.register_url, self.valid_registration_data, HTTP_AUTHORIZATION=Authorization1,
                         format='json')
        self.mentor_data['password'] = Cache.getInstance().get("TOKEN_password_AUTH").decode('utf-8')
        response = self.client.post(self.login_url, self.mentor_data, format='json')
        Authorization2 = response.get('HTTP_AUTHORIZATION')
        response = self.client.delete(self.patch_url, HTTP_AUTHORIZATION=Authorization2, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_delete_with_non_existent_user_should_return_404_NOT_FOUND(self):
        response = self.client.post(self.login_url, self.admin_data, format='json')
        Authorization1 = response.get('HTTP_AUTHORIZATION')
        response = self.client.delete(self.invalid_patch_url, HTTP_AUTHORIZATION=Authorization1, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_token_returns_400_BAD_REQUEST(self):  # DECODE ERROR
        response = self.client.post(self.login_url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        Authorization = response.get('HTTP_AUTHORIZATION').replace("m","M")
        response = self.client.get(self.get_url, HTTP_AUTHORIZATION=Authorization, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_reset_email_for_valid_email(self):
        response = self.client.post(self.reset_email_url,self.email_data,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_send_reset_email_for_invalid_email_returns_400_BAD_REQUEST(self):
        response = self.client.post(self.reset_email_url,self.invalid_email_data,format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_for_valid_email(self):
        client=APIClient()
        self.client.post(self.reset_email_url,self.email_data,format='json')
        url=Cache.getInstance().get("REDIRECT_1_URL").decode('utf-8')
        response = client.patch(url, self.password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_reset_password_cache_contains_no_token_returns_401_UNAUTHORIZED(self):
        client=APIClient()
        self.client.post(self.reset_email_url,self.email_data,format='json')
        Cache.getInstance().delete("RESET_1_TOKEN")
        url=Cache.getInstance().get("REDIRECT_1_URL").decode('utf-8')
        response = client.patch(url, self.password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_reset_password_cache_contains_wrong_token_returns_400_BAD_REQUEST(self):
        client=APIClient()
        self.client.post(self.reset_email_url,self.email_data,format='json')
        invalid_token=Cache.getInstance().get("RESET_1_TOKEN").decode('utf-8').replace("m","M")
        Cache.getInstance().set("RESET_1_TOKEN",invalid_token)
        url=Cache.getInstance().get("REDIRECT_1_URL").decode('utf-8')
        response = client.patch(url, self.password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_reset_password_for_password_length_less_than_2_returns_400_BAD_REQUEST(self):
        client=APIClient()
        self.client.post(self.reset_email_url,self.email_data,format='json')
        url=Cache.getInstance().get("REDIRECT_1_URL").decode('utf-8')
        response = client.patch(url, self.invalid_password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
