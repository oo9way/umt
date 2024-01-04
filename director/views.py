from datetime import datetime
from django.shortcuts import render
from django.views.generic import ListView
from django.shortcuts import redirect
from django.urls import reverse

from director.permissions import IsDirectorRole
from materials.models import Design, Expenditure, Finance, LabelStorage, MaterialStorage, Product, ProductSalesCard, ProductSalesHistory, ProductStock, SpareStorage
from superuser.forms import ExpenditureForm, FinanceForm, InsertLabel, InsertMaterialForm, InsertSpare
from django.db.models import Sum, Q, F, ExpressionWrapper
from django.db.models.fields import IntegerField
from django.contrib import messages

# Create your views here.
class HomePageView(IsDirectorRole, ListView):
    model = MaterialStorage
    paginate_by = 20
    template_name = "superadmin/home.html"

    def post(self, request, *args, **kwargs):
        MaterialStorage.import_material(request)
        return redirect(reverse("director:dashboard"))

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["insert_material_form"] = InsertMaterialForm
        return context_data

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by("-id").filter(is_active="active")
        return queryset




class SpareListView(IsDirectorRole, ListView):
    model = SpareStorage
    paginate_by = 20
    template_name = "superadmin/spare/home.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by("-id").filter(is_active="active")
        return queryset
    
    

class LabelListView(IsDirectorRole, ListView):
    model = LabelStorage
    paginate_by = 20
    template_name = "superadmin/label/home.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by("-id").filter(is_active="active")
        return queryset




def admin_pre_production_send_list(request):
    products = Product.objects.all()
    designs = Design.objects.all()

    context = {
        'products': products,
        'designs': designs
    }
    return render(request, 'superadmin/production/sendlist.html', context)


class StockView(IsDirectorRole, ListView):
    model = ProductStock
    paginate_by = 20
    ordering = ["-id"]
    template_name = "superadmin/stock/list_create.html"



def admin_sales(request):
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    if not request.user.is_authenticated and (request.user.role != 'DIRECTOR'):
        return redirect('users:login')

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
                
                Finance.objects.create(
                    executor=request.user,
                    cost=request.POST['taken_cost'],
                    comment=f"Qarz olindi {card.client}",
                    type="debit"
                    
                )
                
                messages.success(request, "Muvaffaqiyatli saqlandi")
        except:
            messages.error(
                request, 'Nimadir xato ketdi, qaytadan urining', extra_tags='danger')
        return redirect('director:sales')

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
    
    if not request.user.is_authenticated and (request.user.role != 'DIRECTOR'):
        return redirect('users:login')
    
    
    query = ProductSalesHistory.objects.all()
    date_from = request.GET.get('start')
    date_to = request.GET.get('end')
    
    if not request.user.is_authenticated and request.user.role != "ADMIN":
        return redirect(reverse('users:login'))
    
    if date_from:
        query = ProductSalesHistory.objects.filter(created_at__gte=date_from)
        
    if request.GET.get('end'):
        query = ProductSalesHistory.objects.filter(created_at__lte=date_to)
        
    
    context = {
        'query': query.order_by('-created_at')
    }
    return render(request, 'superadmin/stock/history.html', context)





class ExpenditureView(IsDirectorRole, ListView):
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
                        
            Finance.objects.create(
                executor=self.request.user,
                cost=expenditure.cost,
                comment=f"Harajat - {expenditure.comment}",
            )
            return redirect("director:expenditure")
        
        
        
class FinanceView(IsDirectorRole, ListView):
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
            return redirect("director:finance")
