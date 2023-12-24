from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import ListView, View, UpdateView, DeleteView
from superuser.permissions import IsAdminRole
from materials.models import *
from superuser.forms import *
from django.shortcuts import get_object_or_404


class HomePageView(IsAdminRole, ListView):
    model = MaterialStorage
    paginate_by = 20
    template_name = "superadmin/home.html"

    def post(self, request, *args, **kwargs):
        MaterialStorage.import_material(request)
        return redirect(reverse("superuser:dashboard"))

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["insert_material_form"] = InsertMaterialForm
        return context_data

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by("-id").filter(is_active="active")
        return queryset


class MaterialTypeListView(IsAdminRole, ListView):
    model = MaterialType
    template_name = "superadmin/materialtypes.html"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by("-id")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = InsertMaterialTypeForm
        return context

    def post(self, request, *args, **kwargs):
        form = InsertMaterialTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("superuser:material_types"))


class MaterialTypeUpdateView(IsAdminRole, UpdateView):
    model = MaterialType
    fields = ["name"]
    labels = {"name": "Material Type"}
    success_url = reverse_lazy("superuser:material_types")
    template_name = "superadmin/materialtype_form.html"


class MaterialTypeDeleteView(IsAdminRole, DeleteView):
    model = MaterialType
    success_url = reverse_lazy("superuser:material_types")
    template_name = "superadmin/materialtype_confirm_delete.html"


class MaterialHistoryListView(IsAdminRole, ListView):
    model = MaterialStorageHistory
    template_name = "superadmin/materialhistory.html"
    paginate_by = 20
    ordering = ["-updated_at"]


class MaterialInActivesListView(IsAdminRole, ListView):
    model = MaterialStorage
    paginate_by = 20
    template_name = "superadmin/inactive_materials.html"

    def get_queryset(self):
        queryset = super().get_queryset().order_by("-id")
        queryset = queryset.filter(is_active="pending")
        return queryset


class MaterialInActiveUpdateView(IsAdminRole, UpdateView):
    model = MaterialStorage
    fields = ["price", "confirmed_price", "price_type"]
    success_url = reverse_lazy("superuser:material_inactives")
    template_name = "superadmin/inactive_material_form.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_active="pending")
        return queryset

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.is_active = "active"
        instance.save()
        MaterialStorage.accept_material(self.request, instance)

        return super().form_valid(form)


class MaterialInActiveCancelView(IsAdminRole, UpdateView):
    model = MaterialStorage
    fields = []
    success_url = reverse_lazy("superuser:material_inactives")
    template_name = "superadmin/inactive_material_cancel_form.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_active="pending")
        return queryset

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.is_active = "inactive"
        instance.save()
        MaterialStorage.cancel_material(self.request, instance)

        return super().form_valid(form)


class SpareListView(IsAdminRole, ListView):
    model = SpareStorage
    paginate_by = 20
    template_name = "superadmin/spare/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = InsertSpare
        return context

    def post(self, request, *args, **kwargs):
        SpareStorage.import_spare(request)
        return redirect(reverse("superuser:spare_list"))

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by("-id").filter(is_active="active")
        return queryset


class SpareTypeListView(IsAdminRole, ListView):
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
            return redirect(reverse("superuser:spare_types"))


class SpareTypeUpdateView(IsAdminRole, UpdateView):
    model = SpareType
    fields = ["name"]
    success_url = reverse_lazy("superuser:spare_types")
    template_name = "superadmin/spare/spare_type_form.html"


class SpareTypeDeleteView(IsAdminRole, DeleteView):
    model = SpareType
    success_url = reverse_lazy("superuser:spare_types")
    template_name = "superadmin/spare/spare_type_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["restricted"] = SpareStorage.objects.filter(spare=obj).exists()
        return context


class SpareHistoryListView(IsAdminRole, ListView):
    model = SpareStorageHistory
    template_name = "superadmin/spare/spare_history.html"
    paginate_by = 20
    ordering = ["-created_at"]


class SpareExportView(IsAdminRole, ListView):
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

        return redirect(reverse("superuser:spare_export"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.query
        context["found"] = self.found
        context["where"] = WHERE

        return context


class LabelListView(IsAdminRole, ListView):
    model = LabelStorage
    paginate_by = 20
    template_name = "superadmin/label/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = InsertLabel
        return context

    def post(self, request, *args, **kwargs):
        LabelStorage.import_label(request)
        return redirect(reverse("superuser:label_list"))

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by("-id").filter(is_active="active")
        return queryset


class LabelTypeListView(IsAdminRole, ListView):
    model = LabelType
    template_name = "superadmin/label/label_types.html"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by("-id")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = InsertLabelTypeForm
        return context

    def post(self, request, *args, **kwargs):
        form = InsertLabelTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("superuser:label_types"))


class LabelTypeUpdateView(IsAdminRole, UpdateView):
    model = LabelType
    fields = ["name"]
    success_url = reverse_lazy("superuser:label_types")
    template_name = "superadmin/label/label_type_form.html"


class LabelTypeDeleteView(IsAdminRole, DeleteView):
    model = LabelType
    success_url = reverse_lazy("superuser:label_types")
    template_name = "superadmin/label/label_type_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["restricted"] = LabelStorage.objects.filter(label=obj).exists()
        return context


class LabelHistoryListView(IsAdminRole, ListView):
    model = LabelStorageHistory
    template_name = "superadmin/label/label_history.html"
    paginate_by = 20
    ordering = ["-created_at"]


class LabelExportView(IsAdminRole, ListView):
    query = False
    found = False
    template_name = "superadmin/label/export.html"
    model = LabelStorage
    paginate_by = 50

    def get(self, request, *args, **kwargs):
        title = self.request.GET.get("title", None)
        if title:
            self.query = True
            self.queryset = LabelStorage.objects.filter(
                label__name__icontains=title, is_active="active"
            )
            self.found = self.queryset.exists()

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        obj = self.request.POST.get("object", None)
        amount = self.request.POST.get("amount", None)
        where = self.request.POST.get("where", None)

        label = get_object_or_404(LabelStorage, pk=obj)
        if float(label.amount) >= float(amount):
            label.export(request.user, amount, where)

        return redirect(reverse("superuser:label_export"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.query
        context["found"] = self.found
        context["where"] = WHERE

        return context
