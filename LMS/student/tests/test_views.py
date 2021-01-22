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
        self.student_register_url = reverse("student-register")
        self.single_student_url = reverse("student-details", kwargs={"pk": 1})


class StudentDetailsTest(Data):

    def test_student_with_valid_details(self):
        self.valid_registration_data = {
            "name": "Astroboy",
            "phone_number": "9876543210",
            "alternate_contact_number": "9517538524",
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
            'masters': 'Mtech'
        }

        self.valid_patch_data = {
            "name": "Astrogirl"
        }
        response = self.client.post(self.student_register_url, self.valid_registration_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.single_student_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.patch(self.single_student_url, self.valid_patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
