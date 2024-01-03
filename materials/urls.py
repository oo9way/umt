from django.urls import path
from materials.views import HomePageView, MaterialHistoryListView, MaterialInActivesListView

app_name = 'materials'

urlpatterns = [
    path("dashboard/", HomePageView.as_view(), name="dashboard"),
    path("dashboard/inactives/", MaterialInActivesListView.as_view(),name="inactives"),
    path("dashboard/history/", MaterialHistoryListView.as_view(), name="history"),
    
]