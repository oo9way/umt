from django.urls import path
from user.views import MainLoginView

app_name = "users"

urlpatterns = [path("login/", MainLoginView.as_view(), name="login")]
