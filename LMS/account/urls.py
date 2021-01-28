from .views import *        #LoginUser, RegisterUser
from django.conf import settings
from django.urls.conf import path
from django.conf.urls import url, re_path


app_name = "account"

urlpatterns = [
    path('register', RegisterUser.as_view(), name="register_user"),
    path('update/<int:pk>', RegisterUser.as_view(), name="update_user"),
    path('delete/<int:pk>', RegisterUser.as_view(), name="delete_user"),
    path('users', RegisterUser.as_view(), name="get_users"),
    path('login', LoginUser.as_view(), name="login_user"),
    path('logout', LoginUser.as_view(), name="logout_user"),
    path('request_reset', RequestPasswordResetEmail.as_view(),name="generate_reset_password_link"),
    re_path(r'^reset/(?P<reset_token>.*)$', SetNewPassword.as_view(),name="reset_password"),
   ]

