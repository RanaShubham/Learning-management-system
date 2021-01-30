from django.urls import reverse, resolve



class TestUrls:
    def test_mentor_post_url(self):
        path = reverse("mentor:post_mentor")
        assert resolve(path).view_name == "mentor:post_mentor"

    def test_admin_get_mentors_url(self):
        path = reverse("mentor:get_mentors")
        assert resolve(path).view_name == "mentor:get_mentors"

    def test_get_or_delete_specific_mentor_url(self):
        path = reverse("mentor:get_delete_mentor", kwargs={'pk': 1})
        assert resolve(path).view_name == "mentor:get_delete_mentor"

