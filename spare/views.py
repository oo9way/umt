from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect

from materials.models import SpareStorage, SpareStorageHistory, SpareType
from spare.permissions import IsSpareRole
from superuser.forms import InsertSpare, InsertSpareTypeForm
from materials.models import WHERE

# Create your views here.
class SpareListView(IsSpareRole, ListView):
    model = SpareStorage
    paginate_by = 20
    template_name = "superadmin/spare/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = InsertSpare
        return context

    def post(self, request, *args, **kwargs):
        SpareStorage.import_spare(request)
        return redirect(reverse("spare:dashboard"))

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by("-id").filter(is_active="active")
        return queryset


class SpareTypeListView(IsSpareRole, ListView):
    model = SpareType
    template_name = "superadmin/spare/spare_types.html"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by("-id")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = InsertSpareTypeForm
        return context

    def post(self, request, *args, **kwargs):
        form = InsertSpareTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("spare:spare_types"))


class SpareTypeUpdateView(IsSpareRole, UpdateView):
    model = SpareType
    fields = ["name"]
    success_url = reverse_lazy("spare:spare_types")
    template_name = "superadmin/spare/spare_type_form.html"


class SpareTypeDeleteView(IsSpareRole, DeleteView):
    model = SpareType
    success_url = reverse_lazy("superuser:spare_types")
    template_name = "superadmin/spare/spare_type_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["restricted"] = SpareStorage.objects.filter(spare=obj).exists()
        return context


class SpareHistoryListView(IsSpareRole, ListView):
    model = SpareStorageHistory
    template_name = "superadmin/spare/spare_history.html"
    paginate_by = 20
    ordering = ["-created_at"]


class SpareExportView(IsSpareRole, ListView):
    query = False
    found = False
    template_name = "superadmin/spare/export.html"
    model = SpareStorage
    paginate_by = 50

    def get(self, request, *args, **kwargs):
        barcode = self.request.GET.get("barcode", None)
        if barcode:
            self.query = True
            self.queryset = SpareStorage.objects.filter(
                barcode=barcode, is_active="active"
            )
            self.found = self.queryset.exists()

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        obj = self.request.POST.get("object", None)
        amount = self.request.POST.get("amount", None)
        where = self.request.POST.get("where", None)

        spare = get_object_or_404(SpareStorage, pk=obj)
        if float(spare.amount) >= float(amount):
            spare.export(request.user, amount, where)

        return redirect(reverse("spare:spare_export"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.query
        context["found"] = self.found
        context["where"] = WHERE

        return context

