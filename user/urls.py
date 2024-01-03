from django.urls import path
from user.views import MainLoginView, MainLogoutView

app_name = "users"

urlpatterns = [
    path("login/", MainLoginView.as_view(), name="login"),
    path("login/", MainLogoutView.as_view(), name="logout")
]
