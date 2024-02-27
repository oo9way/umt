from materials.models import *
from superuser.permissions import IsAdminRole
from django.views import View
from superuser.resources import *
from django.http import HttpResponse


class GenerateMaterialExcel(View):
    def get(self, request, *args, **kwargs):
        dataset = MaterialModelResource().export(
            MaterialStorage.objects.all().order_by("-id")
        )
        response = HttpResponse(dataset.xls, content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = 'attachment; filename="homashyo ombori.xls"'
        return response


class GenerateMaterialHistoryExcel(View):
    def get(self, request, *args, **kwargs):
        dataset = MaterialHistoryModelResource().export(
            MaterialStorageHistory.objects.all().order_by("-id")
        )
        response = HttpResponse(dataset.xls, content_type="application/vnd.ms-excel")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="homashyo ombori tarixi.xls"'
        return response


class GenerateSpareExcel(View):
    def get(self, request, *args, **kwargs):
        dataset = SpareModelResource().export(
            SpareStorage.objects.all().order_by("-id")
        )
        response = HttpResponse(dataset.xls, content_type="application/vnd.ms-excel")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="ehtiyot qism ombori.xls"'
        return response


class GenerateSpareHistoryExcel(View):
    def get(self, request, *args, **kwargs):
        dataset = SpareHistoryModelResource().export(
            SpareStorageHistory.objects.all().order_by("-id")
        )
        response = HttpResponse(dataset.xls, content_type="application/vnd.ms-excel")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="ehtiyot qism ombori tarixi.xls"'
        return response


class GenerateLabelExcel(View):
    def get(self, request, *args, **kwargs):
        dataset = LabelModelResource().export(
            LabelStorage.objects.all().order_by("-id")
        )
        response = HttpResponse(dataset.xls, content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = 'attachment; filename="etiketika ombori.xls"'
        return response


class GenerateLabelHistoryExcel(View):
    def get(self, request, *args, **kwargs):
        
        dataset = LabelHistoryModelResource().export(
            LabelStorageHistory.objects.all().order_by("-id")
        )
        response = HttpResponse(dataset.xls, content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = 'attachment; filename="etiketika tarixi.xls"'
        return response



class GenerateDesignExcel(View):
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
        response["Content-Disposition"] = 'attachment; filename="Dizaynlar.xls"'
        return response
        
        
class GenerateDesignPriceHistoryExcel(IsAdminRole, View):
    def get(self, request, *args, **kwargs):
        queryset = DesignPriceHistory.objects.all().order_by("-id")
        

        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        name = self.request.GET.get("name")
    
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)

        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
            
        if name:
            queryset = queryset.filter(design_name__icontains=name)
    

        dataset = DesignPriceHistoryModelResource().export(
            queryset
        )
        
        
        response = HttpResponse(dataset.xls, content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = 'attachment; filename="Dizaynlar narxlar tarixi.xlsx"'
        return response




class GenerateExpenditureExcel(View):
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
        response["Content-Disposition"] = 'attachment; filename="Harajatlar.xls"'
        return response


class GenerateFinanceExcel(View):
    def get(self, request, *args, **kwargs):
        queryset = Finance.objects.all().order_by("-id")
        
        date_from = self.request.GET.get('date_from', None)
        date_to = self.request.GET.get('date_to', None)
        
        dataset = FinanceModelResource().export(
            queryset
        )

        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
            
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
            
        
        response = HttpResponse(dataset.xls, content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = 'attachment; filename="kirim-chiqimlar.xls"'
        return response
