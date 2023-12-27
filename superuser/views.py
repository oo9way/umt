from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import ListView, View, UpdateView, DeleteView
from superuser.permissions import IsAdminRole
from materials.models import *
from superuser.forms import *
from django.shortcuts import get_object_or_404
from django.contrib import messages


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


class DesignView(IsAdminRole, ListView):
    model = Design
    paginate_by = 20
    ordering = ["-created_at"]
    template_name = "superadmin/design/list_create.html"

    def post(self, request, *args, **kwargs):
        form = AdminDesign(request.POST)
        design = form.save(commit=False)
        design.save()
        design_id = design.id
        return redirect(reverse("superuser:design-insert-materials", args=(design_id,)))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AdminDesign
        return context


def admin_insert_design_materials(request, pk):
    try:
        design = Design.objects.get(id=pk)
        form = InlineDesignField(
            queryset=DesignField.objects.filter(design_type=design), instance=design
        )

    except:
        messages.error(
            request, "Formada xatolik bor, qaytadan urining", extra_tags="danger"
        )
        return redirect("superuser:design_home")
    
    if design.designfield_set.count() > 0:
        return redirect("superuser:design_home")

    if request.method == "POST":
        form = InlineDesignField(request.POST, instance=design)
        if form.is_valid():
            form.save()
            for i in range(1, 7):
                if request.POST[f"label{i}"] != "":
                    label = LabelType.objects.get(id=request.POST[f"label{i}"])
                    dlb = DesignLabel.objects.create(design=design, label=label)
                    if request.POST[f"label{i}_amount"] != "":
                        price = float(request.POST[f"label{i}_amount"])
                        dlb.price = price
                        dlb.save()

            if request.POST["salary_amount"] != "":
                try:
                    salary_amount = float(request.POST["salary_amount"])
                except:
                    salary_amount = 0
            else:
                salary_amount = 0

            salary_calc_type = request.POST["salary_calc_type"]
            DesignImmutable.objects.create(
                name="Ish haqqi",
                calc_type=salary_calc_type,
                cost=salary_amount,
                design=design,
                task="salary",
            )

            if request.POST["energy_amount"] != "":
                try:
                    energy_amount = float(request.POST["energy_amount"])
                except:
                    energy_amount = 0
            else:
                energy_amount = 0
            energy_calc_type = request.POST["energy_calc_type"]
            DesignImmutable.objects.create(
                name="Elektr energiya va gaz",
                calc_type=energy_calc_type,
                cost=energy_amount,
                design=design,
                task="energy",
            )

            if request.POST["oil_amount"] != "":
                try:
                    oil_amount = float(request.POST["oil_amount"])
                except:
                    oil_amount = 0
            else:
                oil_amount = 0
            oil_calc_type = request.POST["oil_calc_type"]
            DesignImmutable.objects.create(
                name="Moy",
                calc_type=oil_calc_type,
                cost=oil_amount,
                design=design,
                task="oil",
            )

            if request.POST["brak_amount"] != "":
                try:
                    brak_amount = float(request.POST["brak_amount"])
                except:
                    brak_amount = 0
            else:
                brak_amount = 0
            brak_calc_type = request.POST["brak_calc_type"]
            DesignImmutable.objects.create(
                name="Brak",
                calc_type=brak_calc_type,
                cost=brak_amount,
                design=design,
                task="brak",
            )

            if request.POST["different_amount"] != "":
                try:
                    different_amount = float(request.POST["different_amount"])
                except:
                    different_amount = 0
            else:
                different_amount = 0
            different_calc_type = request.POST["different_calc_type"]
            DesignImmutable.objects.create(
                name="Har xil",
                calc_type=different_calc_type,
                cost=different_amount,
                design=design,
                task="different",
            )

            if request.POST["anothers_amount"] != "":
                try:
                    anothers_amount = float(request.POST["anothers_amount"])
                except:
                    anothers_amount = 0
            else:
                anothers_amount = 0
            anothers_calc_type = request.POST["anothers_calc_type"]
            DesignImmutable.objects.create(
                name="Qo'shimcha",
                calc_type=anothers_calc_type,
                cost=anothers_amount,
                design=design,
                task="anothers",
            )

            if request.POST["building_amount"] != "":
                try:
                    building_amount = float(request.POST["building_amount"])
                except:
                    building_amount = 0
            else:
                building_amount = 0

            building_calc_type = request.POST["building_calc_type"]
            DesignImmutable.objects.create(
                name="Amortizatsiya bino",
                calc_type=building_calc_type,
                cost=building_amount,
                design=design,
                task="building",
            )

            if request.POST["stanok_amount"] != "":
                try:
                    stanok_amount = float(request.POST["stanok_amount"])
                except:
                    stanok_amount = 0
            else:
                stanok_amount = 0
            stanok_calc_type = request.POST["stanok_calc_type"]
            DesignImmutable.objects.create(
                name="Amortizatsiya stanok",
                calc_type=stanok_calc_type,
                cost=stanok_amount,
                design=design,
                task="stanok",
            )

            if request.POST["addition_amount"] != "":
                try:
                    addition_amount = float(request.POST["addition_amount"])
                except:
                    addition_amount = 0
            else:
                addition_amount = 0
            addition_calc_type = request.POST["addition_calc_type"]
            DesignImmutable.objects.create(
                name="Boshqa",
                calc_type=addition_calc_type,
                cost=addition_amount,
                design=design,
                task="addition",
            )

            messages.success(request, "Dizayn muvaffaqiyatli kiritildi")
        else:
            messages.error(request, "Formada xatolik bor")

        return redirect("superuser:design_home")

    context = {"menu": "design", "form": form, "labels": LabelType.objects.all()}

    return render(request, "superadmin/design/insert_material.html", context)


def admin_edit_design_materials(request, pk):
    try:
        design = Design.objects.get(id=pk)
        form = InlineDesignField(
            queryset=DesignField.objects.filter(design_type=design), instance=design
        )

    except:
        messages.error(
            request, "Formada xatolik bor, qaytadan urining", extra_tags="danger"
        )
        return redirect("base:admin-design")

    if request.method == "POST":
        form = InlineDesignField(request.POST, instance=design)
        if form.is_valid():
            form.save()
            for i in range(1, 7):
                if request.POST[f"label{i}"] != "":
                    try:
                        if request.POST[f"label{i}_id"] != "":
                            if request.POST[f"label{i}"] == "cancel":
                                dlb_item = DesignLabel.objects.get(
                                    id=request.POST[f"label{i}_id"]
                                )
                                dlb_item.delete()
                                dlb = False
                            else:
                                dlb = DesignLabel.objects.get(
                                    id=request.POST[f"label{i}_id"]
                                )
                        else:
                            label = LabelType.objects.get(id=request.POST[f"label{i}"])
                            dlb = DesignLabel.objects.create(design=design, label=label)

                        if request.POST[f"label{i}_amount"] != "" and dlb != False:
                            try:
                                price = float(request.POST[f"label{i}_amount"])
                                dlb.price = price
                                dlb.save()
                            except:
                                pass

                    except:
                        pass

            if request.POST["salary_amount"] != "":
                try:
                    salary_amount = float(request.POST["salary_amount"])
                except:
                    salary_amount = 0
            else:
                salary_amount = 0

            salary_calc_type = request.POST["salary_calc_type"]
            get_salary, salary_created = DesignImmutable.objects.get_or_create(
                design=design, task="salary", name="Ish haqqi"
            )
            get_salary.calc_type = salary_calc_type
            get_salary.cost = salary_amount
            get_salary.save()

            if request.POST["energy_amount"] != "":
                try:
                    energy_amount = float(request.POST["energy_amount"])
                except:
                    energy_amount = 0
            else:
                energy_amount = 0

            energy_calc_type = request.POST["energy_calc_type"]
            get_energy, energy_created = DesignImmutable.objects.get_or_create(
                design=design, task="energy", name="Elektr energiya va gaz"
            )
            get_energy.calc_type = energy_calc_type
            get_energy.cost = energy_amount
            get_energy.save()

            if request.POST["oil_amount"] != "":
                try:
                    oil_amount = float(request.POST["oil_amount"])
                except:
                    oil_amount = 0
            else:
                oil_amount = 0

            oil_calc_type = request.POST["oil_calc_type"]
            get_oil, oil_created = DesignImmutable.objects.get_or_create(
                design=design, task="oil", name="Moy"
            )
            get_oil.calc_type = oil_calc_type
            get_oil.cost = oil_amount
            get_oil.save()

            if request.POST["brak_amount"] != "":
                try:
                    brak_amount = float(request.POST["brak_amount"])
                except:
                    brak_amount = 0
            else:
                brak_amount = 0

            brak_calc_type = request.POST["brak_calc_type"]
            get_brak, brak_created = DesignImmutable.objects.get_or_create(
                design=design, task="brak", name="Brak"
            )
            get_brak.calc_type = brak_calc_type
            get_brak.cost = brak_amount
            get_brak.save()

            if request.POST["different_amount"] != "":
                try:
                    different_amount = float(request.POST["different_amount"])
                except:
                    different_amount = 0
            else:
                different_amount = 0

            different_calc_type = request.POST["different_calc_type"]
            get_different, different_created = DesignImmutable.objects.get_or_create(
                design=design, task="different", name="Har xil"
            )
            get_different.calc_type = different_calc_type
            get_different.cost = different_amount
            get_different.save()

            if request.POST["anothers_amount"] != "":
                try:
                    anothers_amount = float(request.POST["anothers_amount"])
                except:
                    anothers_amount = 0
            else:
                anothers_amount = 0

            anothers_calc_type = request.POST["anothers_calc_type"]
            get_anothers, anothers_created = DesignImmutable.objects.get_or_create(
                design=design, task="anothers", name="Qo'shimcha"
            )
            get_anothers.calc_type = anothers_calc_type
            get_anothers.cost = anothers_amount
            get_anothers.save()

            if request.POST["building_amount"] != "":
                try:
                    building_amount = float(request.POST["building_amount"])
                except:
                    building_amount = 0
            else:
                building_amount = 0

            building_calc_type = request.POST["building_calc_type"]
            get_building, building_created = DesignImmutable.objects.get_or_create(
                design=design, task="building", name="Amortizatsiya bino"
            )
            get_building.calc_type = building_calc_type
            get_building.cost = building_amount
            get_building.save()

            if request.POST["stanok_amount"] != "":
                try:
                    stanok_amount = float(request.POST["stanok_amount"])
                except:
                    stanok_amount = 0
            else:
                stanok_amount = 0
            stanok_calc_type = request.POST["stanok_calc_type"]
            get_stanok, stanok_created = DesignImmutable.objects.get_or_create(
                design=design, task="stanok", name="Amortizatsiya stanok"
            )
            get_stanok.calc_type = stanok_calc_type
            get_stanok.cost = stanok_amount
            get_stanok.save()

            if request.POST["addition_amount"] != "":
                try:
                    addition_amount = float(request.POST["addition_amount"])
                except:
                    addition_amount = 0
            else:
                addition_amount = 0
            addition_calc_type = request.POST["addition_calc_type"]
            get_addition, addition_created = DesignImmutable.objects.get_or_create(
                design=design, task="addition", name="Boshqa"
            )
            get_addition.calc_type = addition_calc_type
            get_addition.cost = addition_amount
            get_addition.save()

            messages.success(request, "Dizayn muvaffaqiyatli kiritildi")
        else:
            messages.error(request, "Formada xatolik bor")

        return redirect("superuser:design_home")

    context = {
        "menu": "design",
        "form": form,
        "design": design,
        "labels": LabelType.objects.all(),
    }

    return render(request, "superadmin/design/edit_material.html", context)


def admin_design_details(request, pk):
    design = Design.objects.get(id=pk)
    immutables = ImmutableBalance.objects.all()
    exchange = Exchange.objects.last()
    context = {'design': design, 'immutables': immutables, 'exchange':exchange}
    return render(request, 'superadmin/design/details.html', context)


class DesignDeleteView(IsAdminRole, DeleteView):
    model = Design
    success_url = reverse_lazy("superuser:design_home")
    template_name = "superadmin/design/delete.html"