from .views import *
from django.conf import settings
from django.urls.conf import path
from django.conf.urls import url, re_path


app_name = "account"

urlpatterns = [
    path('role', CreateRole.as_view(), name="get_post_role"),
    path('users', GetUsers.as_view(), name="get_users"),
    path('user', RegisterUser.as_view(), name="post_user"),
    path('user/<int:pk>', UpdateUser.as_view(), name="update_delete_user"),
    path('login', LoginUser.as_view(), name="login_user"),
    path('logout', LogoutUser.as_view(), name="logout_user"),
    path('request_reset', RequestPasswordResetEmail.as_view(),name="generate_reset_password_link"),
    re_path(r'^reset/(?P<reset_token>.*)$', SetNewPassword.as_view(),name="reset_password"),
   ]

