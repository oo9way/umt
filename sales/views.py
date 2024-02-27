from datetime import datetime
from typing import Any
from uuid import uuid4
from django.forms.models import BaseModelForm

from django.http import HttpRequest, HttpResponse
from materials.models import ProductSales, ProductSalesCard, ProductSalesHistory, ProductStock, Design
from django.views.generic import ListView, CreateView
from sales.forms import ProductStockForm
from sales.permissions import IsSalerRole
import json
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.db import transaction
from django.db.models import Sum, Q, F, ExpressionWrapper
from django.db.models.fields import IntegerField


# Create your views here.
class StockView(IsSalerRole, ListView):
    model = ProductStock
    paginate_by = 20
    ordering = ["-id"]
    template_name = "superadmin/stock/list_create.html"


def stock_sell(request):
    if not request.user.is_authenticated and request.user.role != "SALES":
        return redirect(reverse('users:login'))

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
                return redirect('sales:stock-sell')

        if all(has == True for has in all_has):
            client = data["client"]
            contract_id = data["sale_number"]
            contract_date = data["sale_date"]
            client_address = data["client_address"]
            phone_number = data["phone_number"]

            card = ProductSalesCard.objects.create(
                card_id=uuid4(),
                given_cost=data['given_cost'],
                client=client,
                contract_id=contract_id,
                contract_date=contract_date,
                address=client_address,
                phone_number=phone_number

            )
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
                        return redirect('sales:stock-sell')
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
        return redirect('sales:stock-remove')

    context = {
        'materials': materials,
    }
    if 'success' in request.GET:
        if request.GET['success'] == 'true':
            messages.success(request, 'Muvaffaqiyatli yuborildi')
    return render(request, 'superadmin/stock/sell.html', context)


def remove_local_storage(request):
    my_url = reverse('sales:stock-sell')
    return render(request, 'superadmin/stock/remove.html', {'my_url': my_url})


def sales(request):
    current_month = datetime.now().month
    current_year = datetime.now().year

    if not request.user.is_authenticated and request.user.role != "SALES":
        return redirect(reverse('users:login'))

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
        return redirect('sales:sales')

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
        'total_sales': total_sales

    }
    return render(request, 'superadmin/stock/index.html', context)


def sales_history(request):
    if not request.user.is_authenticated and request.user.role != "SALES":
        return redirect(reverse('users:login'))

    query = ProductSalesHistory.objects.all()
    date_from = request.GET.get('start')
    date_to = request.GET.get('end')

    if date_from:
        query = ProductSalesHistory.objects.filter(created_at__gte=date_from)

    if request.GET.get('end'):
        query = ProductSalesHistory.objects.filter(created_at__lte=date_to)

    context = {
        'query': query.order_by('-created_at')
    }
    return render(request, 'superadmin/stock/history.html', context)


class StockBarcodeView(IsSalerRole, ListView):
    model = ProductStock
    template_name = "superadmin/stock/barcodes.html"


class CreateProductStockView(IsSalerRole, CreateView):
    template_name = 'sales/create.html'
    form_class = ProductStockForm
    success_url = reverse_lazy('sales:stock-create')

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.is_active = "active"
        instance.price = instance.design.total

        instance.save()

        return super().form_valid(form)
