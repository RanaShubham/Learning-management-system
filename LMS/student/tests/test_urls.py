from django.urls import reverse, resolve


class TestUrls:
    def test_register_url(self):
        path = reverse("student-register")
        assert resolve(path).view_name == "student-register"

    def test_login_url(self):
        path = reverse("student-details", kwargs={"pk": 1})
        assert resolve(path).view_name == "student-details"
