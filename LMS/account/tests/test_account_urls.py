from django.urls import reverse, resolve


class TestUrls:
    def test_register_url(self):
        path = reverse("account:post_user")
        assert resolve(path).view_name == "account:post_user"

    def test_get_url(self):
        path = reverse("account:get_users")
        assert resolve(path).view_name == "account:get_users"

    def test_update_url(self):
        path = reverse("account:update_delete_user", kwargs={'pk':1})
        assert resolve(path).view_name == "account:update_delete_user"

    def test_login_url(self):
        path = reverse("account:login_user")
        assert resolve(path).view_name == "account:login_user"
    
    def test_logout_url(self):
        path = reverse("account:logout_user")
        assert resolve(path).view_name == "account:logout_user"
    
    def test_generate_reset_password_url(self):
        path = reverse("account:generate_reset_password_link")
        assert resolve(path).view_name == "account:generate_reset_password_link"