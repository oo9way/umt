from django.contrib import admin
from materials.models import *

# Register your models here.
admin.site.register([MaterialStorage, MaterialType, MaterialStorageHistory])
admin.site.register([SpareStorage, SpareType, SpareStorageHistory])
admin.site.register([LabelStorage, LabelType, LabelStorageHistory])
admin.site.register([Exchange, Design, DesignField, DesignImmutable, DesignLabel, ProductStock])
admin.site.register([ProductionMaterialStorage, Brak, Worker, Product, WorkerAccount, WorkerWork])
