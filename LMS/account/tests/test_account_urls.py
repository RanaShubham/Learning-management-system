from django.urls import reverse, resolve


class TestUrls:
    def test_register_url(self):
        print('hi'*50)
        path = reverse("account:register_get_update_delete", kwargs={'pk':''})
        print(path, "path here")
        assert resolve(path).view_name == "account:register_get_update_delete"

    def test_login_url(self):
        path = reverse("account:login_user")
        assert resolve(path).view_name == "account:login_user"
    
    def test_logout_url(self):
        path = reverse("account:logout_user")
        assert resolve(path).view_name == "account:logout_user"
    
    def test_generate_reset_password_url(self):
        path = reverse("account:generate_reset_password_link")
        assert resolve(path).view_name == "account:generate_reset_password_link"