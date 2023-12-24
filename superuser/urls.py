from django.urls import path
from superuser.views import (
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
    SpareListView,
    SpareTypeDeleteView,
    SpareTypeListView,
    SpareTypeUpdateView,
    SpareHistoryListView,
    SpareExportView,
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

# SPARE VIEWS
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
]
