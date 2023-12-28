from materials.models import *
from superuser.permissions import IsAdminRole
from django.views import View
from superuser.resources import *
from django.http import HttpResponse


class GenerateMaterialExcel(IsAdminRole, View):
    def get(self, request, *args, **kwargs):
        dataset = MaterialModelResource().export(
            MaterialStorage.objects.all().order_by("-id")
        )
        response = HttpResponse(dataset.xls, content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = 'attachment; filename="homashyo ombori.xlsx"'
        return response


class GenerateMaterialHistoryExcel(IsAdminRole, View):
    def get(self, request, *args, **kwargs):
        dataset = MaterialHistoryModelResource().export(
            MaterialStorageHistory.objects.all().order_by("-id")
        )
        response = HttpResponse(dataset.xls, content_type="application/vnd.ms-excel")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="homashyo ombori tarixi.xlsx"'
        return response


class GenerateSpareExcel(IsAdminRole, View):
    def get(self, request, *args, **kwargs):
        dataset = SpareModelResource().export(
            SpareStorage.objects.all().order_by("-id")
        )
        response = HttpResponse(dataset.xls, content_type="application/vnd.ms-excel")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="ehtiyot qism ombori.xlsx"'
        return response


class GenerateSpareHistoryExcel(IsAdminRole, View):
    def get(self, request, *args, **kwargs):
        dataset = SpareHistoryModelResource().export(
            SpareStorageHistory.objects.all().order_by("-id")
        )
        response = HttpResponse(dataset.xls, content_type="application/vnd.ms-excel")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="ehtiyot qism ombori tarixi.xlsx"'
        return response


class GenerateLabelExcel(IsAdminRole, View):
    def get(self, request, *args, **kwargs):
        dataset = LabelModelResource().export(
            LabelStorage.objects.all().order_by("-id")
        )
        response = HttpResponse(dataset.xls, content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = 'attachment; filename="etiketika ombori.xlsx"'
        return response


class GenerateLabelHistoryExcel(IsAdminRole, View):
    def get(self, request, *args, **kwargs):
        
        dataset = LabelHistoryModelResource().export(
            LabelStorageHistory.objects.all().order_by("-id")
        )
        response = HttpResponse(dataset.xls, content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = 'attachment; filename="etiketika tarixi.xlsx"'
        return response



class GenerateDesignExcel(IsAdminRole, View):
    def get(self, request, *args, **kwargs):
        queryset = Design.objects.all().order_by("-id")
        
        title = self.request.GET.get('name', None)
        sex = self.request.GET.get('sex', None)
        season = self.request.GET.get('season', None)
        
        dataset = DesignModelResource().export(
            queryset
        )

        if title:
            queryset = queryset.filter(name__icontains=title)
            
        if sex:
            queryset = queryset.filter(sex=sex)
            
        if season:
            queryset = queryset.filter(season=season)
        
        response = HttpResponse(dataset.xls, content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = 'attachment; filename="Dizaynlar.xlsx"'
        return response



class GenerateExpenditureExcel(IsAdminRole, View):
    def get(self, request, *args, **kwargs):
        queryset = Expenditure.objects.all().order_by("-id")
        
        date_from = self.request.GET.get('date_from', None)
        date_to = self.request.GET.get('date_to', None)
        
        dataset = ExpenditureModelResource().export(
            queryset
        )

        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
            
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
            
        
        response = HttpResponse(dataset.xls, content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = 'attachment; filename="Harajatlar.xlsx"'
        return response
