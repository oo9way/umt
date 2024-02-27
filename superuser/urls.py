from django.urls import path
from superuser.forms import SellBrak
from superuser.views import (
    BrakListView,
    DesignPriceHistoryView,
    DesignView,
    ExpenditureView,
    FinanceView,
    HomePageView,
    LabelExportView,
    LabelHistoryListView,
    LabelListView,
    LabelTypeDeleteView,
    LabelTypeListView,
    LabelTypeUpdateView,
    MaterialInActiveCancelView,
    MaterialInActiveUpdateView,
    MaterialTypeListView,
    MaterialTypeUpdateView,
    MaterialTypeDeleteView,
    MaterialHistoryListView,
    MaterialInActivesListView,
    ProductionMaterialHistory,
    SellBrakView,
    SpareListView,
    SpareTypeDeleteView,
    SpareTypeListView,
    SpareTypeUpdateView,
    SpareHistoryListView,
    SpareExportView,
    DesignDeleteView,
    StockBarcodeView,
    StockView,
    UserView,
    WorkerListCreateView,
    admin_account_details,
    admin_accounts_history,
    admin_design_details,
    admin_edit_design_materials,
    admin_insert_design_materials,
    admin_pre_production_send,
    admin_pre_production_send_list,
    admin_sales,
    admin_unclosed_salaries,
    admin_worker_account,
    admin_worker_credits,
    admin_worker_details,
    admin_worker_stats,
    admin_workers,
    production_send_yaim,
    remove_local_storage,
    sales_history,
    stock_sell,
)

from superuser.utils.generate_xls import *

app_name = "superuser"

urlpatterns = [
    path("dashboard/", HomePageView.as_view(), name="dashboard"),
    path(
        "dashboard/material-types/",
        MaterialTypeListView.as_view(),
        name="material_types",
    ),
    path(
        "dashboard/material-types/edit/<int:pk>/",
        MaterialTypeUpdateView.as_view(),
        name="material_types_update",
    ),
    path(
        "dashboard/material-types/delete/<int:pk>/",
        MaterialTypeDeleteView.as_view(),
        name="material_types_delete",
    ),
    path(
        "dashboard/history/",
        MaterialHistoryListView.as_view(),
        name="material_history",
    ),
    path(
        "dashboard/material/inactives/",
        MaterialInActivesListView.as_view(),
        name="material_inactives",
    ),
    path(
        "dashboard/material/inactives/confirm/<int:pk>/",
        MaterialInActiveUpdateView.as_view(),
        name="material_inactives_confirm",
    ),
    path(
        "dashboard/material/inactives/cancel/<int:pk>/",
        MaterialInActiveCancelView.as_view(),
        name="material_inactives_cancel",
    ),
]

# SPARE VIEWS
urlpatterns += [
    path("dashboard/spare/", SpareListView.as_view(), name="spare_list"),
    path("dashboard/spare/types/", SpareTypeListView.as_view(), name="spare_types"),
    path(
        "dashboard/spare/types/edit/<int:pk>/",
        SpareTypeUpdateView.as_view(),
        name="spare_types_update",
    ),
    path(
        "dashboard/spare/types/delete/<int:pk>/",
        SpareTypeDeleteView.as_view(),
        name="spare_types_delete",
    ),
    path(
        "dashboard/spare/history/",
        SpareHistoryListView.as_view(),
        name="spare_history",
    ),
    path(
        "dashboard/spare/export/",
        SpareExportView.as_view(),
        name="spare_export",
    ),
]

# LABEL VIEWS
urlpatterns += [
    path("dashboard/label/", LabelListView.as_view(), name="label_list"),
    path("dashboard/label/types/", LabelTypeListView.as_view(), name="label_types"),
    path(
        "dashboard/label/types/edit/<int:pk>/",
        LabelTypeUpdateView.as_view(),
        name="label_types_update",
    ),
    path(
        "dashboard/label/types/delete/<int:pk>/",
        LabelTypeDeleteView.as_view(),
        name="label_types_delete",
    ),
    path(
        "dashboard/label/history/",
        LabelHistoryListView.as_view(),
        name="label_history",
    ),
    path(
        "dashboard/label/export/",
        LabelExportView.as_view(),
        name="label_export",
    ),
]

# DESIGN VIEWS
urlpatterns += [
    path("dashboard/design/home/", DesignView.as_view(), name="design_home"),
    path(
        "dashboard/design/insert-materials/<int:pk>/",
        admin_insert_design_materials,
        name="design-insert-materials",
    ),
    path(
        "dashboard/design/edit-materials/<int:pk>/",
        admin_edit_design_materials,
        name="design-edit-materials",
    ),

    path(
        "dashboard/design/details/<int:pk>/",
        admin_design_details,
        name="design-details",
    ),
    path("dashboard/design/delete/<int:pk>/", DesignDeleteView.as_view(), name="design_delete"),
    path("dashboard/design/price/history/", DesignPriceHistoryView.as_view(), name="design_price_history"),

]

urlpatterns += [
    path("dashboard/production/material/history/", ProductionMaterialHistory.as_view(),
         name="production_material_history"),
    path("dashboard/production/brak/", BrakListView.as_view(), name="brak_list"),
    path("dashboard/production/brak/sell/<int:pk>/", SellBrakView.as_view(), name="sell_brak"),
    path("dashboard/production/send-yaim/", production_send_yaim, name="send_yaim"),
]

urlpatterns += [
    path("dashboard/expenditure/", ExpenditureView.as_view(), name="expenditure"),
]

urlpatterns += [
    path("dashboard/profiles/", UserView.as_view(), name="profiles"),
]

# FINANCE
urlpatterns += [
    path("dashboard/finance/", FinanceView.as_view(), name="finance"),
]

# PRE PRODUCTION
urlpatterns += [
    path("dashboard/pre-production/", admin_pre_production_send_list, name="pre-production"),
    path('dashboard/pre-production/send-list/<int:pk>', admin_pre_production_send,
         name='pre-production-send'),
]

# WORKERS

urlpatterns += [
    path("dashboard/workers/", admin_workers, name="workers"),
    path('dashboard/workers/<int:pk>/', admin_worker_details, name='worker-details'),
    path('dashboard/workers/account/<int:pk>/', admin_worker_account, name='worker-accounts'),
    path('dashboard/workers/account-details/<int:pk>/', admin_account_details, name='worker-account'),
    path('dashboard/workers/account/<int:wid>/stats/<int:aid>/', admin_worker_credits, name='worker-stats'),
    path('dashboard/workers/unclosed-accounts/', admin_unclosed_salaries, name='unclosed-accounts'),
    path('dashboard/workers/history/', admin_accounts_history, name='accounts-history'),
    path('dashboard/workers/stats/', admin_worker_stats, name='register-workers-stats'),
]

# STOCK

urlpatterns += [
    path("dashboard/stock/", StockView.as_view(), name="stock"),
    path("dashboard/stock/sell/", stock_sell, name="stock-sell"),
    path('dashboard/stock/remove/', remove_local_storage, name='stock-remove'),
    path('dashboard/sales/', admin_sales, name='sales'),
    path('dashboard/sales/history', sales_history, name='sales-history'),

    path("dashboard/stock/barcodes/", StockBarcodeView.as_view(), name="stock-barcodes"),
]

# EXCEL GENERATORS
urlpatterns += [
    path(
        "dashboard/material/history/generate-xls/",
        GenerateMaterialHistoryExcel.as_view(),
        name="material_history_xls",
    ),
    path(
        "dashboard/material/generate-xls/",
        GenerateMaterialExcel.as_view(),
        name="material_xls",
    ),
    path(
        "dashboard/spare/history/generate-xls/",
        GenerateSpareHistoryExcel.as_view(),
        name="spare_history_xls",
    ),
    path(
        "dashboard/spare/generate-xls/",
        GenerateSpareExcel.as_view(),
        name="spare_xls",
    ),
    path(
        "dashboard/label/history/generate-xls/",
        GenerateLabelHistoryExcel.as_view(),
        name="label_history_xls",
    ),
    path(
        "dashboard/label/generate-xls/",
        GenerateLabelExcel.as_view(),
        name="label_xls",
    ),

    path(
        "dashboard/design/generate-xls/",
        GenerateDesignExcel.as_view(),
        name="design_xls",
    ),

    path(
        "dashboard/expenditure/generate-xls/",
        GenerateExpenditureExcel.as_view(),
        name="expenditure_xls",
    ),

    path(
        "dashboard/finance/generate-xls/",
        GenerateFinanceExcel.as_view(),
        name="finance_xls",
    ),
    path(
        "dashboard/design/history/generate-xls/",
        GenerateDesignPriceHistoryExcel.as_view(),
        name="design_price_history_xls",
    ),
]

# TODO
# * Nazoratchi / Sotuvchi / Zapchast / Seryo ----> Profillar


# Pul kirimlari
# Brak mahsulot
# Savdo
