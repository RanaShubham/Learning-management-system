from django.urls import reverse, resolve


class TestUrls:
    def test_get_performance_info_url(self):
        path = reverse("performance_info:get_performance_info_all")
        assert resolve(path).view_name == "performance_info:get_performance_info_all"

    def test_add_performance_info_url(self):
        path = reverse("performance_info:post_performance_info")
        assert resolve(path).view_name == "performance_info:post_performance_info"

    def test_update_performance_info_url(self):
        path = reverse("performance_info:update_delete_performance_info", kwargs={"performance_id": 1})
        assert resolve(path).view_name == "performance_info:update_delete_performance_info"