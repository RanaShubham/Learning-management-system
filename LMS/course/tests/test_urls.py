from django.urls import reverse, resolve


class TestUrls:
    def test_register_url(self):
        path = reverse("course-register")
        assert resolve(path).view_name == "course-register"

    def test_login_url(self):
        path = reverse("specific-course", kwargs={"pk": 1})
        assert resolve(path).view_name == "specific-course"