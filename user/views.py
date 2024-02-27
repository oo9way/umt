from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse


class MainLoginView(LoginView):
    template_name = "pages/login.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.user.is_authenticated:
            if self.request.user.role == "ADMIN":
                return redirect(reverse("superuser:dashboard"))
            
            if self.request.user.role == "MATERIAL":
                return redirect(reverse("materials:dashboard"))
            
            if self.request.user.role == "SALES":
                return redirect(reverse("sales:dashboard"))
            
            if self.request.user.role == "SPARE":
                return redirect(reverse("spare:dashboard"))
            
            if self.request.user.role == "DIRECTOR":
                return redirect(reverse("director:dashboard"))
                
            if self.request.user.role == "INACTIVE":
                return redirect(reverse("users:login"))

        return response


class MainLogoutView(LogoutView):
    template_name = 'pages/logout.html'