from django.urls import path

from director.views import ExpenditureView, FinanceView, HomePageView, LabelListView, SpareListView, StockView, admin_pre_production_send_list, admin_sales, sales_history


app_name = 'director'

urlpatterns = [
    path('dashboard/', HomePageView.as_view(), name='dashboard'),
    path("dashboard/spare/", SpareListView.as_view(), name="spare"),
    path("dashboard/label/", LabelListView.as_view(), name="label"),
    path("dashboard/pre-production/", admin_pre_production_send_list, name="pre-production"),
    path("dashboard/stock/", StockView.as_view(), name="stock"),
    path('dashboard/sales/', admin_sales, name='sales'),
    path('dashboard/sales/history', sales_history, name='sales-history'),
    path("dashboard/expenditure/", ExpenditureView.as_view(), name="expenditure"),
    path("dashboard/finance/", FinanceView.as_view(), name="finance"),
    
    
]