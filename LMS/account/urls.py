from .views import LoginUser, RegisterUser
from django.conf import settings
from django.urls.conf import path, re_path

app_name = "account"

urlpatterns = [
    re_path(r'^(?P<pk>[0-9]{0,})$', RegisterUser.as_view(), name="register_get_update_delete"),
    path('login', LoginUser.as_view(), name="login_user"),
    path('logout', LoginUser.as_view(), name="logout_user"),
]