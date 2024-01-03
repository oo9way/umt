from datetime import datetime
import json
from uuid import uuid4
from django.http import JsonResponse
from django.db.models import Sum, Q, F, ExpressionWrapper

from django.http.response import HttpResponse as HttpResponse
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import (
    ListView,
    View,
    UpdateView,
    DeleteView,
    DetailView,
    CreateView,
)
from superuser.permissions import IsAdminRole
from django.db.models.fields import IntegerField

from materials.models import (
    DesignField,
    DesignImmutable,
    DesignLabel,
    DesignPriceHistory,
    Finance,
    MaterialStorage,
    MaterialStorageHistory,
    MaterialType,
    PreProduction,
    PreProductionHistory,
    Product,
    ProductSales,
    ProductSalesCard,
    ProductSalesHistory,
    ProductStock,
    ProductStockHistory,
    ProductionMaterialStorage,
    ProductionMaterialStorageHistory,
    SpareStorage,
    SpareStorageHistory,
    SpareType,
    LabelStorage,
    LabelType,
    LabelStorageHistory,
    Brak,
    Design,
    Expenditure,
    Worker,
    ImmutableBalance,
    Exchange,
    WorkerAccount,
    WorkerCredit,
    WorkerDebit,
    WorkerFine
)
from superuser.utils.check_amount import check_amount, create_price, insert_worker_stats
from user.models import User

from django.db import transaction
from django.db.models import Sum

from superuser.forms import (
    AdminProductStockForm,
    AdminWorker,
    FinanceForm,
    UserForm,
    InsertLabel,
    InsertLabelTypeForm,
    InlineDesignField,
    InsertMaterialForm,
    InsertMaterialTypeForm,
    InsertSpare,
    InsertSpareTypeForm,
    AdminAllImmutables,
    AdminDesign,
    AdminDesignFieldForm,
    AdminImmutables,
    SellBrak,
    ImportMaterialToProduction, 
    ExpenditureForm    
)
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

    def get_queryset(self):
        queryset = super().get_queryset()

        title = self.request.GET.get("name", None)
        sex = self.request.GET.get("sex", None)
        season = self.request.GET.get("season", None)

        if title:
            queryset = queryset.filter(name__icontains=title)

        if sex:
            queryset = queryset.filter(sex=sex)

        if season:
            queryset = queryset.filter(season=season)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AdminDesign

        context["name"] = self.request.GET.get("name", None)
        context["sex"] = self.request.GET.get("sex", None)
        context["season"] = self.request.GET.get("season", None)

        return context


def admin_insert_design_materials(request, pk):
    try:
        design = Design.objects.get(id=pk)

        if design.designfield_set.count() == 0:
            material_type = MaterialType.objects.all()
            design_fields = []
            for mt in material_type:
                design_fields.append(DesignField(material_type=mt, design_type=design))
            DesignField.objects.bulk_create(design_fields)
        return redirect(reverse("superuser:design-edit-materials", args=(pk,)))

    except:
        messages.error(
            request, "Formada xatolik bor, qaytadan urining", extra_tags="danger"
        )
        return redirect("superuser:design_home")


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
            
            create_price(design)

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
    context = {"design": design, "immutables": immutables, "exchange": exchange}
    return render(request, "superadmin/design/details.html", context)


class DesignDeleteView(IsAdminRole, DeleteView):
    model = Design
    success_url = reverse_lazy("superuser:design_home")
    template_name = "superadmin/design/delete.html"



class ProductionMaterialHistory(IsAdminRole, ListView):
    model = ProductionMaterialStorageHistory
    paginate_by = 20
    ordering = ["-created_at"]
    template_name = "superadmin/production/history.html"

    def get_queryset(self):
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        queryset = super().get_queryset()
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)

        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        return queryset


class BrakListView(IsAdminRole, ListView):
    model = Brak
    paginate_by = 20
    ordering = ["-id"]
    template_name = "superadmin/production/brak_list_create.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(status="active")
        return queryset


class SellBrakView(IsAdminRole, DetailView):
    model = Brak
    template_name = "superadmin/production/sell_brak.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = SellBrak
        return context

    def post(self, request, pk, *args, **kwargs):
        brak = Brak.objects.get(id=pk)
        form = SellBrak(request.POST)
        if form.is_valid():
            brak.status = "sold"
            brak.save()
            return redirect("superuser:brak_list")


class ExpenditureView(IsAdminRole, ListView):
    model = Expenditure
    paginate_by = 20
    ordering = ["-id"]
    template_name = "superadmin/production/list_create.html"
    date_from = ""
    date_to = ""

    def get_queryset(self):
        self.date_from = self.request.GET.get("date_from", "")
        self.date_to = self.request.GET.get("date_to", "")
        queryset = super().get_queryset()
        if self.date_from:
            queryset = queryset.filter(created_at__gte=self.date_from)

        if self.date_to:
            queryset = queryset.filter(created_at__lte=self.date_to)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ExpenditureForm
        context["date_from"] = self.date_from
        context["date_to"] = self.date_to
        return context

    def post(self, request, *args, **kwargs):
        form = ExpenditureForm(self.request.POST)
        if form.is_valid():
            expenditure = form.save(commit=False)
            expenditure.executor = self.request.user
            expenditure.save()
            return redirect("superuser:expenditure")


class UserView(IsAdminRole, CreateView):
    model = User
    template_name = "superadmin/user/home.html"
    form_class = UserForm
    success_url = reverse_lazy("superuser:profiles")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])
        user.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_list"] = User.objects.all().order_by("-id")

        return context



@transaction.atomic
def production_send_yaim(request):
    if request.user.is_authenticated and request.user.role == 'ADMIN':
        workers = Worker.objects.all()
        designs = Design.objects.all()
        fields = []
        field = {}

        if request.method == "POST":
            r = int(request.POST['rows_amount'])
            for l in range(1, r+1):
                try:
                    field = {
                        "field_id": l,
                        "date": request.POST['date'],
                        "worker_id": request.POST[f'worker{l}'],
                        "cost": request.POST[f'cost{l}'],
                        "design_id": request.POST[f'design{l}'],
                        "amount": request.POST[f'amount{l}'],
                        "second_type_per": request.POST[f'second_type_per{l}'],
                        "second_type_gr": request.POST[f'second_type_gr{l}'],
                        "third_type": request.POST[f'third_type{l}'],
                    }
                    fields.append(field)
                except:
                    pass
            response = check_amount(fields,request)
            return JsonResponse({'success':True, 'data':response})

        context = {
            'menu': 'production_send',
            'workers': workers,
            'designs': designs
        }

        if 'rows' in request.GET:
            arr = range(1, int(request.GET['rows'])+1)
            context = {
                'menu': 'production_send',
                'workers': workers,
                'designs': designs,
                'rows': arr,
                'rows_amount': request.GET['rows']
            }

        return render(request, 'superadmin/production/send.html', context)
    return redirect('base:login')


class WorkerListCreateView(IsAdminRole, ListView):
    model = Worker
    paginate_by = 20
    ordering = ["-id"]
    template_name = "superadmin/workers/list_create.html"
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['form'] = WorkerForm
        return context
    
    
    

def admin_workers(request):
    current_month = datetime.now().month
    current_year = datetime.now().year

    worker_form = AdminWorker
    workers = Worker.objects.all()

    if request.method == "POST" and request.POST['type'] == 'insert_worker':
        worker_form = AdminWorker(request.POST)
        if worker_form.is_valid():
            worker_form.save()
            messages.success(request, "Ro'yxatdan o'tkazildi")
        else:
            messages.error(request, "Formada xatolik bor", extra_tags='danger')
        return redirect('superuser:workers')

    if request.method == "POST" and request.POST['type'] == 'credits':
        try:
            with transaction.atomic():
                worker_credit = WorkerCredit.objects.create(
                    amount=request.POST['credit_amount'],
                    comment=request.POST['comment']
                )

                worker = Worker.objects.get(id=request.POST['worker_id'])

                worker_accounts = WorkerAccount.objects.filter(
                    created_at__month=current_month, created_at__year=current_year).filter(worker=worker).filter(completed=False)
                if len(worker_accounts) == 1:
                    worker_account = worker_accounts.last()
                elif len(worker_accounts) == 0:
                    worker_account = WorkerAccount.objects.create(
                        worker=worker
                    )

                worker_account.credits_history.add(worker_credit)
                worker_account.credits = float(
                    worker_account.credits) + float(request.POST['credit_amount'])

                worker_account.save()

                # send_msg(
                #     worker.phone, f"Sizga {request.POST['credit_amount']} so'm miqdorida avans berildi.\nUmumiy olingan avans: {worker_account.credits} so'm")
                return redirect("superuser:workers")

        except:
            messages.error(
                request, "Ishchi topilmadi, qaytadan urining", extra_tags='danger')
            return redirect("superuser:workers")

    if request.method == "POST" and request.POST['type'] == 'debits':
        try:
            with transaction.atomic():
                worker_debit = WorkerDebit.objects.create(
                    amount=request.POST['debit_amount'],
                    comment=request.POST['comment']
                )

                worker = Worker.objects.get(id=request.POST['worker_id'])

                worker_accounts = WorkerAccount.objects.filter(
                    created_at__month=current_month, created_at__year=current_year).filter(worker=worker).filter(completed=False)
                if len(worker_accounts) == 1:
                    worker_account = worker_accounts.last()
                elif len(worker_accounts) == 0:
                    worker_account = WorkerAccount.objects.create(
                        worker=worker
                    )

                worker_account.debits_history.add(worker_debit)
                worker_account.debits = float(
                    worker_account.debits) + float(request.POST['debit_amount'])

                worker_account.save()

                # send_msg(
                #     worker.phone, f"Sizga {request.POST['debit_amount']} so'm miqdorida bonus berildi.\nUmumiy olingan bonus: {worker_account.debits} so'm")
                return redirect("superuser:workers")

        except:
            messages.error(
                request, "Ishchi topilmadi, qaytadan urining", extra_tags='danger')
            return redirect("superuser:workers")

    if request.method == "POST" and request.POST['type'] == 'fines':
        try:
            with transaction.atomic():
                worker_fine = WorkerFine.objects.create(
                    amount=request.POST['fine_amount'],
                    comment=request.POST['comment']
                )

                worker = Worker.objects.get(id=request.POST['worker_id'])

                worker_accounts = WorkerAccount.objects.filter(
                    created_at__month=current_month, created_at__year=current_year).filter(worker=worker).filter(completed=False)
                if len(worker_accounts) == 1:
                    worker_account = worker_accounts.last()
                elif len(worker_accounts) == 0:
                    worker_account = WorkerAccount.objects.create(
                        worker=worker
                    )

                worker_account.fines_history.add(worker_fine)
                worker_account.fines = float(
                    worker_account.fines) + float(request.POST['fine_amount'])

                worker_account.save()

                # send_msg(
                #     worker.phone, f"Sizga {request.POST['fine_amount']} so'm miqdorida jarima yozildi.\nUmumiy olingan jarima: {worker_account.fines} so'm")
                return redirect("superuser:workers")

        except:
            messages.error(
                request, "Ishchi topilmadi, qaytadan urining", extra_tags='danger')
            return redirect("superuser:workers")

    context = {
        'menu': 'admin-workers',
        'worker_form': worker_form,
        'workers': workers
    }
    return render(request, "superadmin/workers/index.html", context)



def admin_worker_details(request, pk):

    worker = Worker.objects.get(id=pk)

    form = AdminWorker(instance=worker)

    if request.method == "POST":
        form = AdminWorker(request.POST, instance=worker)
        if form.is_valid():
            form.save()
            messages.success(request, "Muvaffaqiyatli o'zgartirildi")
            return redirect("superuser:workers")

    context = {
        'form': form,
        'worker': worker,
    }
    
    return render(request, 'superadmin/workers/details.html', context)


def admin_worker_account(request, pk):

    worker = Worker.objects.get(id=pk)

    worker_accounts = WorkerAccount.objects.filter(completed=False).filter(worker=worker)

    if len(worker_accounts) == 0:
        wa = WorkerAccount.objects.create(worker=worker)
        worker_accounts = [wa]

    if request.method == "POST":
        with transaction.atomic():
            account = WorkerAccount.objects.get(id=request.POST['account_id'])
            account.completed = True
            account.save()
            if worker.salary_types == 'monthly':
                total_cost = float(worker.salary) - float(account.fines) - float(account.credits) + float(account.debits)
            else:
                total_cost = float(account.workerworks_cost) - float(account.fines) - float(account.credits) + float(account.debits)

            # balance = Balance.objects.get(id=1)
            # balance.uzs_balance = float(balance.uzs_balance) - total_cost
            # balance.save()

            # BalanceHistory.objects.create(
            #     executor=request.user,
            #     transaction_type='credit',
            #     cost=total_cost,
            #     currency='uzs',
            #     comment="Oylik maosh"
            # )

        return redirect("superuser:workers")

    context = {
        'worker': worker,
        'accounts':worker_accounts,
    }

    return render(request, 'superadmin/workers/account.html', context)



def admin_worker_credits(request, wid, aid):
    try:
        if request.GET['type'] == 'credits':
            view_type = 'credits'
        elif request.GET['type'] == 'debits':
            view_type = 'debits'
        elif request.GET['type'] == 'fines':
            view_type = 'fines'
        elif request.GET['type'] == 'works':
            view_type = 'works'

        worker = Worker.objects.get(id=wid)
        worker_account = WorkerAccount.objects.get(id=aid)
        context = {
            'worker':worker,
            'account':worker_account,
            'view':view_type
        }
        return render(request, 'superadmin/workers/all_stats.html', context)
    except:
        return redirect("base:admin-workers")
    
    
    

def admin_unclosed_salaries(request):
    unclosed_accounts = WorkerAccount.objects.filter(completed=False)
    context = {
        'menu':'unclosed',
        'accounts':unclosed_accounts
    }
    return render(request, 'superadmin/workers/unclosed.html', context)




def admin_accounts_history(request):
    query = None
    if 'year' in request.GET and 'month' in request.GET and 'type' in request.GET:
        year = request.GET['year']
        month = request.GET['month']
        a_type = request.GET['type']

        if month == 'all':
            accounts = WorkerAccount.objects.filter(created_at__year=year)
        else:
            accounts = WorkerAccount.objects.filter(created_at__month=month).filter(created_at__year=year)

        if a_type == 'true':
            accounts = accounts.filter(completed=True)
        elif a_type == 'false':
            accounts = accounts.filter(completed=False)
        
        query = accounts

    context = {
        'menu':'account-history',
        'query':query
    }
    return render(request, 'superadmin/workers/history.html', context)



def admin_account_details(request, pk):
    account = WorkerAccount.objects.get(id=pk)
    worker = account.worker

    if request.method == "POST":
        with transaction.atomic():
            account = WorkerAccount.objects.get(id=request.POST['account_id'])
            account.completed = True
            account.save()
            if worker.salary_types == 'monthly':
                total_cost = float(worker.salary) - float(account.fines) - float(account.credits) + float(account.debits)
            else:
                total_cost = float(account.workerworks_cost) - float(account.fines) - float(account.credits) + float(account.debits)

            # balance = Balance.objects.get(id=1)
            # balance.uzs_balance = float(balance.uzs_balance) - total_cost
            # balance.save()

            # BalanceHistory.objects.create(
            #     executor=request.user,
            #     transaction_type='credit',
            #     cost=total_cost,
            #     currency='uzs',
            #     comment="Oylik maosh"
            # )

        return redirect("superuser:worker-account", pk=account.id)



    context = {
        'worker':account.worker,
        'accounts':[account]
    }
    return render(request, 'superadmin/workers/account.html', context)




def admin_worker_stats(request):
    workers = Worker.objects.all()

    fields = []
    field = {}

    if request.method == "POST":
        r = int(request.POST['rows_amount'])
        for l in range(1, r+1):
            try:
                field = {
                    "field_id": l,
                    "worker_id": request.POST[f'worker{l}'],
                    "cost": request.POST[f'cost{l}'],
                    "amount": request.POST[f'amount{l}'],
                }
                print(field)
                fields.append(field)
            except:
                pass
        response = insert_worker_stats(fields, request)
        return JsonResponse({'success': True, 'data': response})

    context = {
        'menu': 'workers-stats',
        'workers': workers,
    }

    if 'rows' in request.GET:
        arr = range(1, int(request.GET['rows'])+1)
        context = {
            'menu': 'production_send',
            'workers': workers,
            'rows': arr,
            'rows_amount': request.GET['rows']
        }
    return render(request, 'superadmin/workers/stats.html', context)




class FinanceView(IsAdminRole, ListView):
    model = Finance
    paginate_by = 20
    ordering = ["-id"]
    template_name = "superadmin/finance/list_create.html"
    date_from = ""
    date_to = ""

    def get_queryset(self):
        self.date_from = self.request.GET.get("date_from", "")
        self.date_to = self.request.GET.get("date_to", "")
        queryset = super().get_queryset()
        if self.date_from:
            queryset = queryset.filter(created_at__gte=self.date_from)

        if self.date_to:
            queryset = queryset.filter(created_at__lte=self.date_to)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = FinanceForm
        context["date_from"] = self.date_from
        context["date_to"] = self.date_to
        return context

    def post(self, request, *args, **kwargs):
        form = FinanceForm(self.request.POST)
        if form.is_valid():
            finance = form.save(commit=False)
            finance.executor = self.request.user
            finance.save()
            return redirect("superuser:finance")




def admin_pre_production_send_list(request):
    products = Product.objects.all()
    designs = Design.objects.all()

    if request.method == "POST" and request.POST['type'] == 'export':
        if request.POST['brak'] == 'second':
            with transaction.atomic():
                design = Design.objects.get(id=request.POST['design'])
                product = Product.objects.get(design_type=design)
                old_brak = Brak.objects.filter(design=design).filter(
                    status='active').filter(sort_type='second')

                if request.POST['per_amount'] != '' and float(request.POST['per_amount']) > 0:
                    c_per_amount = float(request.POST['per_amount'])
                    if float(product.amount) < float(request.POST['per_amount']):
                        messages.error(
                            request, 'Ushbu miqdorda brak mahsulot mavjud emas', extra_tags='danger')
                        return redirect('superuser:pre-production')

                    product.amount = float(
                        product.amount) - float(request.POST['per_amount'])
                    product.save()

                    if len(old_brak) > 0:
                        first_brak = old_brak.first()
                        # old_brak.gr_amount = float(
                        #     old_brak.gr_amount) + float(request.POST['gr_amount'])
                        first_brak.per_amount = float(
                            first_brak.per_amount) + float(request.POST['per_amount'])
                        first_brak.save()
                else:
                    c_per_amount = 0

                if request.POST['gr_amount'] != '' and float(request.POST['gr_amount']) > 0:
                    c_gr_amount = float(request.POST['gr_amount'])
                    gramm = 0
                    for d in design.designfield_set.all():
                        gramm += float(d.amount) / float(design.amount)
                    print(gramm)

                    per_amount = int(float(request.POST['gr_amount']) / gramm)
                    if float(product.amount) < per_amount:
                        messages.error(
                            request, 'Ushbu miqdorda brak mahsulot mavjud emas', extra_tags='danger')
                        return redirect('superuser:]pre-production')

                    product.amount = float(product.amount) - per_amount
                    product.save()

                    if len(old_brak) > 0:
                        first_brak = old_brak.first()
                        first_brak.gr_amount = float(
                            first_brak.gr_amount) + float(request.POST['gr_amount'])
                        first_brak.save()
                else:
                    c_gr_amount = 0

                if len(old_brak) == 0:
                    Brak.objects.create(
                        design=design,
                        gr_amount=c_gr_amount,
                        per_amount=c_per_amount,
                        status='active',
                        sort_type='second'
                    )
                brak_amount = f"{c_gr_amount} gramm, {per_amount} dona"

        if request.POST['brak'] == 'third':
            with transaction.atomic():
                design = Design.objects.get(id=request.POST['design'])
                product = Product.objects.get(design_type=design)
                old_brak = Brak.objects.filter(design=design).filter(
                    status='active').filter(sort_type='third')

                if request.POST['gr_amount'] != '' and float(request.POST['gr_amount']) > 0:
                    gramm = 0
                    for d in design.designfield_set.all():
                        gramm += float(d.amount) / float(design.amount)

                    per_amount = int(float(request.POST['gr_amount']) / gramm)
                    if float(product.amount) < per_amount:
                        messages.error(
                            request, 'Ushbu miqdorda brak mahsulot mavjud emas', extra_tags='danger')
                        return redirect('superuser:pre-production')

                    product.amount = float(product.amount) - per_amount
                    product.save()

                    if len(old_brak) > 0:
                        first_brak = old_brak.first()
                        first_brak.gr_amount = float(
                            first_brak.gr_amount) + float(request.POST['gr_amount'])
                        first_brak.save()
                    else:
                        Brak.objects.create(
                            design=design,
                            gr_amount=request.POST['gr_amount'],
                            per_amount=0,
                            status='active',
                            sort_type='third'
                        )
                    brak_amount = request.POST['gr_amount']

        PreProductionHistory.objects.create(
            executor=request.user,
            action='export',
            amount=brak_amount,
            amount_type='gr',
            price=0,
            price_type='usd',
            where='brak',
        )

        messages.success(request, 'Brak mahsulot chiqarildi')
        return redirect('superuser:pre-production')

    context = {
        'products': products,
        'designs': designs
    }
    return render(request, 'superadmin/production/sendlist.html', context)



def admin_pre_production_send(request, pk):
    if request.user.is_authenticated and (request.user.role == 'ADMIN'):
        product = Product.objects.get(id=pk)
        form = AdminProductStockForm
        spare = SpareStorage.objects.filter(
            is_active="active").filter(spare__name__istartswith='salafan')
        
        if request.method == "POST":
            form = AdminProductStockForm(data=request.POST)
            
            all_products = float(
                request.POST['set_amount']) * float(request.POST['product_per_set'])
            
            labels = DesignLabel.objects.filter(design=product.design_type)
            
            labels_amount = []
            
            for l in labels:
                if LabelStorage.objects.filter(label=l.label).aggregate(Sum('amount'))['amount__sum'] >= all_products:
                    labels_amount.append(True)
                    
            if not all(labels_amount):
                messages.error(
                    request, 'Yetarli etiketika mavjud emas', extra_tags='danger')
                return redirect('superuser:pre-production')
                
            
            if form.is_valid() and all_products > 0:
                
                selected_spare = SpareStorage.objects.get(id=request.POST['spare'])
                selected_design = Product.objects.get(id=pk)

                if all_products > float(selected_design.amount):
                    messages.error(
                        request, 'Yetarli mahsulot mavjud emas', extra_tags='danger')
                    return redirect('superuser:pre-production')

                elif float(request.POST['set_amount']) > float(selected_spare.amount):
                    messages.error(
                        request, 'Yetarli salafan mavjud emas', extra_tags='danger')
                    return redirect('superuser:pre-production')

                else:
                    with transaction.atomic():
                        design = Design.objects.get(id=product.design_type.id)

                        old_stock = ProductStock.objects.filter(design__id=design.id).filter(price=product.price).filter(
                            price_type='uzs').filter(product_per_set=request.POST['product_per_set']).filter(
                                confirmed_price=request.POST['confirmed_price']).filter(
                                    is_active='active')
                        
                        if len(old_stock) > 0:
                            old_one = old_stock.first()
                            old_one.set_amount = float(
                                old_one.set_amount) + float(request.POST['set_amount'])
                            old_one.save()
                        else:
                            stock = form.save(commit=False)
                            stock.design = product.design_type
                            stock.price_type = 'uzs'
                            stock.price = product.price
                            stock.is_active = 'active'
                            stock.save()
                            
                            
                        for lb in labels:
                            if all_products <=0:
                                break
                            
                            lb_items = LabelStorage.objects.filter(label=lb.label)
                            
                            rm_amount = all_products
                            
                            for lb_item in lb_items:    
                                a_to_sub = min(all_products, float(lb_item.amount))
                                lb_item.amount = float(lb_item.amount) - a_to_sub
                                lb_item.save()
                                rm_amount = rm_amount - a_to_sub
                                

                            LabelStorageHistory.objects.create(
                                executor=request.user,
                                label=lb_item.label,
                                action="export",
                                amount=rm_amount,
                                price=lb_item.price,
                                price_type=lb_item.price_type,
                                amount_type=lb_item.amount_type,
                                where="yaim",
                            )

                        if float(selected_spare.amount) - float(request.POST['set_amount']) == 0:
                            selected_spare.delete()
                        elif float(selected_spare.amount) - float(request.POST['set_amount']):
                            selected_spare.amount = float(
                                selected_spare.amount) - float(request.POST['set_amount'])
                            selected_spare.save()

                        if float(selected_design.amount) - all_products == 0:
                            selected_design.delete()
                        elif float(selected_design.amount) - all_products > 0:
                            selected_design.amount = float(
                                selected_design.amount) - all_products
                            selected_design.save()

                        ProductStockHistory.objects.create(
                            executor=request.user,
                            action='import',
                            item=design.name,
                            amount=float(
                                request.POST['product_per_set']) * float(request.POST['set_amount']),
                            price=product.price,
                            where='storage',
                        )
                        messages.success(
                            request, "Mahsulot muvaffaqiyatli yuborildi.")
                        return redirect('superuser:pre-production')
            messages.error(request, "Formada xatolik bor.", extra_tags='danger')

            return redirect('superuser:pre-production')
        context = {
            'menu': 'production_send',
            'form': form,
            'spares': spare,
            'product': product
        }

        return render(request, 'superadmin/production/sendpp.html', context)
    return redirect('base:login')



class StockView(IsAdminRole, ListView):
    model = ProductStock
    paginate_by = 20
    ordering = ["-id"]
    template_name = "superadmin/stock/list_create.html"



class StockBarcodeView(IsAdminRole, ListView):
    model = ProductStock
    template_name = "superadmin/stock/barcodes.html"
    
    
def stock_sell(request):
    materials = ProductStock.objects.filter(is_active='active')

    if request.method == "POST":
        data = json.loads(request.POST['data'])
        items = data['items']
        all_has = []
        
        for item in items:
            try:
                st = ProductStock.objects.get(id=item['products'])
                if float(st.set_amount) >= float(item['amount']):
                    all_has.append(True)
                else:
                    all_has.append(False)

            except:
                messages.error(
                    request, 'Nimadir xatolik ketdi, qaytadan urining', extra_tags='danger')
                return redirect('base:admin-stock-sell')

        if all(has == True for has in all_has):
            client = request.POST.get("client")
            print(request.POST)
            print(client)
            card = ProductSalesCard.objects.create(
                card_id=uuid4(), given_cost=data['given_cost'], client=client)
            cost_total = 0

            for item in items:
                with transaction.atomic():
                    in_stock = ProductStock.objects.get(
                        id=item['products'])
                    if float(in_stock.set_amount) - float(item['amount']) == 0:
                        in_stock.is_active = 'deleted'
                        in_stock.set_amount = 0
                    elif float(in_stock.set_amount) - float(item['amount']) < 0:
                        messages.error(
                            request, "Yetarli miqdorda tayyor mahsulot mavjud emas", extra_tags='danger')
                        return redirect('base:admin-stock-sell')
                    else:
                        in_stock.set_amount = float(
                            in_stock.set_amount) - float(item['amount'])

                    in_stock.save()

                    cost_total += float(item['total'])

                    ProductSales.objects.create(
                        card=card,
                        product=in_stock,
                        cost=item['total'],
                        discount=item['discount'],
                        amount=item['amount'],
                        per_set=item['peramount']
                    )
            card.cost = cost_total
            card.save()

            if float(card.cost) == float(data['given_cost']):
                status = 'complete'
            else:
                status = 'start'

            ProductSalesHistory.objects.create(
                card=card,
                taken_cost=data['given_cost'],
                end_cost=float(cost_total) - float(data['given_cost']),
                status=status
            )

            messages.success(request, "Mahsulot yuborildi")

        else:
            messages.error(
                request, "Yetarli mahsulot mavjud emas", extra_tags='danger')
        return redirect('superuser:stock-remove')


    context = {
        'materials': materials,
    }
    if 'success' in request.GET:
        if request.GET['success'] == 'true':
            messages.success(request, 'Muvaffaqiyatli yuborildi')
    return render(request, 'superadmin/stock/sell.html', context)



def remove_local_storage(request):
    my_url = reverse('superuser:stock-sell')
    return render(request, 'superadmin/stock/remove.html', {'my_url': my_url})




def admin_sales(request):
    current_month = datetime.now().month
    current_year = datetime.now().year

    if request.method == "POST":
        try:
            card = ProductSalesCard.objects.get(card_id=request.POST['card'])
            if float(request.POST['taken_cost']) > float(card.cost) - float(card.given_cost):
                messages.error(request, "To`lov summasi xato kiritilgan")
            else:
                card.given_cost = float(
                    card.given_cost) + float(request.POST['taken_cost'])
                card.save()

                if float(card.cost) - float(card.given_cost) == 0:
                    status = 'end'
                else:
                    status = 'process'

                ProductSalesHistory.objects.create(
                    card=card,
                    taken_cost=float(request.POST['taken_cost']),
                    end_cost=float(card.cost) - float(card.given_cost),
                    status=status
                )
                messages.success(request, "Muvaffaqiyatli saqlandi")
        except:
            messages.error(
                request, 'Nimadir xato ketdi, qaytadan urining', extra_tags='danger')
        return redirect('superuser:sales')

    duplicates = ProductSalesCard.objects.annotate(
        diff=ExpressionWrapper(F('cost'), output_field=IntegerField(
        )) - ExpressionWrapper(F('given_cost'), output_field=IntegerField())
    ).filter(~Q(diff=0))

    finished_sales = ProductSalesCard.objects.annotate(
        diff=ExpressionWrapper(F('cost'), output_field=IntegerField(
        )) - ExpressionWrapper(F('given_cost'), output_field=IntegerField())
    ).filter(Q(diff=0)).filter(created_at__month=current_month, created_at__year=current_year)
    
    if 'date' in request.GET and request.GET['date'] != '':
        start_month_str = request.GET.get('date')
        start_month = datetime.strptime(start_month_str, '%Y-%m')
        start_year = start_month.year
        start_month_number = start_month.month
        finished_sales = ProductSalesCard.objects.annotate(
            diff=ExpressionWrapper(F('cost'), output_field=IntegerField(
            )) - ExpressionWrapper(F('given_cost'), output_field=IntegerField())
        ).filter(Q(diff=0)).filter(created_at__month=start_month_number, created_at__year=start_year)

    total_sales = finished_sales.aggregate(Sum('given_cost'))['given_cost__sum']
    context = {
        'unfinished_sales': duplicates.order_by('-id'),
        'finished_sales': finished_sales.order_by('-id'),
        'total_sales':total_sales

    }
    return render(request, 'superadmin/stock/index.html', context)



def sales_history(request):
    query = ProductSalesHistory.objects.all()
    date_from = request.GET.get('start')
    date_to = request.GET.get('end')
    
    if not request.user.is_authenticated and request.user.role != "ADMIN":
        return redirect(reverse('users:login'))
    
    if date_from:
        query = ProductSalesHistory.objects.filter(created_at__gte=date_from)
        
    if request.GET.get('end'):
        query = ProductSalesHistory.objects.filter(created_at__lte=date_to)
        
        
    print(request.GET.get('end'))
    
        
    
    context = {
        'query': query.order_by('-created_at')
    }
    return render(request, 'superadmin/stock/history.html', context)




class DesignPriceHistoryView(IsAdminRole, ListView):
    model = DesignPriceHistory
    paginate_by = 20
    ordering = ["-created_at"]
    template_name = "superadmin/design/history.html"

    def get_queryset(self):
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        name = self.request.GET.get("name")
        queryset = super().get_queryset()
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)

        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
            
        if name:
            queryset = queryset.filter(design_name__icontains=name)

        return queryset
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        name = self.request.GET.get("name")
        
        context['name'] = name
        context['date_from'] = date_from
        context['date_to'] = date_to
        
        
        return context
    