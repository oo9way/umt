from django.urls import path

from spare.views import SpareExportView, SpareHistoryListView, SpareListView, SpareTypeDeleteView, SpareTypeListView, SpareTypeUpdateView

app_name = 'spare'

# SPARE VIEWS
urlpatterns = [
    path("dashboard/spare/", SpareListView.as_view(), name="dashboard"),
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