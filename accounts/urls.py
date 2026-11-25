from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = "accounts"

urlpatterns = [
    path(
        'login/',
        LoginView.as_view(template_name="login.html"),
        name='login_page'
    ),

    path("logout/", LogoutView.as_view(), name="logout"),

    path("users/", views.UsersPage.as_view(), name="users_page"),
]