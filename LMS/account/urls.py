from .views import GetUser, LoginUser, RegisterUser, UpdateUser
from django.conf import settings
from django.urls.conf import path

app_name = "account"

urlpatterns = [
    path('', GetUser.as_view(), name="get_users"),
    path('register', RegisterUser.as_view(), name="regsiter_user"),
    path('login', LoginUser.as_view(), name="login_user"),
    path('update/<int>', UpdateUser.as_view(), name="update_user"),
]