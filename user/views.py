from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse


class MainLoginView(LoginView):
    template_name = "pages/login.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.user.is_authenticated:
            if self.request.user.role == "ADMIN":
                return redirect(reverse("superuser:dashboard"))

        return response
