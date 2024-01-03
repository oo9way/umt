from django.shortcuts import render
from materials.models import MaterialStorage, MaterialStorageHistory
from materials.permissions import IsMaterialRole
from superuser.forms import InsertMaterialForm
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic import ListView

# Create your views here.

class HomePageView(IsMaterialRole, ListView):
    model = MaterialStorage
    paginate_by = 20
    template_name = "superadmin/home.html"

    def post(self, request, *args, **kwargs):
        MaterialStorage.import_material(request)
        return redirect(reverse("materials:dashboard"))

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["insert_material_form"] = InsertMaterialForm
        return context_data

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by("-id").filter(is_active="active")
        return queryset
    
    
    
class MaterialInActivesListView(IsMaterialRole, ListView):
    model = MaterialStorage
    paginate_by = 20
    template_name = "superadmin/inactive_materials.html"

    def get_queryset(self):
        queryset = super().get_queryset().order_by("-id")
        queryset = queryset.filter(is_active="pending")
        return queryset
    
    
    
class MaterialHistoryListView(IsMaterialRole, ListView):
    model = MaterialStorageHistory
    template_name = "superadmin/materialhistory.html"
    paginate_by = 20
    ordering = ["-updated_at"]
    