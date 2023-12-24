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
        ] = 'attachment; filename="homashyo ombori tarixi.xlsx"'
        return response
