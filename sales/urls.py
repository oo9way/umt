from django.urls import path

from sales.views import StockBarcodeView, StockView, remove_local_storage, sales, sales_history, stock_sell

app_name = "sales"

urlpatterns = [
    path("dashboard/", StockView.as_view(), name="dashboard"),
    path("dashboard/stock/sell/", stock_sell, name="stock-sell"),
    path('dashboard/stock/remove/', remove_local_storage, name='stock-remove'),
    path('dashboard/sales/', sales, name='sales'),
    path('dashboard/sales/history', sales_history, name='sales-history'),
    path("dashboard/stock/barcodes/", StockBarcodeView.as_view(), name="stock-barcodes"),
    
    
    
]