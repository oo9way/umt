from django.db import models
from user.models import User

AMOUNTS = (
    ("gram", "Gramm"),
    ("liter", "Litr"),
    ("kg", "Kilogramm"),
    ("point", "Dona"),
    ("meter", "Metr"),
)
CURRENCIES = (
    ("uzs", "UZS"),
    ("usd", "USD"),
)

ACTIVE = (("active", "Faol"), ("inactive", "Nofaol"), ("pending", "Kutilmoqda"))

ACTION_TYPES = (
    ("import", "Kirim"),
    ("export", "Chiqim"),
    ("update", "Yangilash"),
    ("delete", "O'chirish"),
    ("cancel", "Bekor qilish"),
    ("sold", "Sotish"),
    ("confirm", "Tasdiqlash"),
)

WHERE = (
    ("null", "--------"),
    ("material", "Homashyo ombori"),
    ("label", "Etiketika ombori"),
    ("production", "Ishlab chiqarish"),
    ("spare", "Ehtiyot qism ombori"),
    ("yaim", "Yarim tayyor mahsulot"),
    ("product", "Tayyor mahsulot ombori"),
    ("storage", "Mahsulot ombori"),
)


# MATERIAL TYPES, STORAGE AND HISTORY
class MaterialType(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class MaterialStorageHistory(models.Model):
    executor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    material = models.ForeignKey(MaterialType, on_delete=models.SET_NULL, null=True)

    action = models.CharField(choices=ACTION_TYPES, max_length=9)
    amount = models.CharField(default="0", max_length=255)
    amount_type = models.CharField(choices=AMOUNTS, max_length=5, default="meter")
    price = models.CharField(max_length=255, blank=True)
    price_type = models.CharField(choices=CURRENCIES, default="usd", max_length=5)
    where = models.CharField(choices=WHERE, max_length=16, default="null")

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class MaterialStorage(models.Model):
    material = models.ForeignKey(MaterialType, on_delete=models.PROTECT)

    amount = models.CharField(default="0", max_length=255)
    amount_type = models.CharField(choices=AMOUNTS, max_length=5)

    price = models.CharField(max_length=600, default=0, verbose_name="Narx")
    confirmed_price = models.CharField(
        max_length=600, default=0, verbose_name="Tasdiqlangan narx"
    )
    price_type = models.CharField(
        choices=CURRENCIES, default="usd", max_length=3, verbose_name="Pul birligi"
    )

    is_active = models.CharField(choices=ACTIVE, default="pending", max_length=8)

    import_comment = models.CharField(max_length=255, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.material} - {self.amount} {self.get_amount_type_display()}"

    @classmethod
    def import_material(cls, request):
        material_type_id = request.POST.get("material")
        price = request.POST.get("price")
        confirmed_price = request.POST.get("confirmed_price")
        price_type = request.POST.get("price_type")
        amount_type = request.POST.get("amount_type")

        material_type = MaterialType.objects.get(id=material_type_id)

        material = MaterialStorage.objects.filter(
            material=material_type,
            price=price,
            confirmed_price=confirmed_price,
            price_type=price_type,
            amount_type=amount_type,
            is_active="active",
        )

        if material.exists():
            m = material.first()
            m.amount = int(m.amount) + int(request.POST.get("amount"))
            m.import_comment = request.POST.get("import_comment")
            m.save()

        else:
            MaterialStorage.objects.create(
                material=material_type,
                amount=int(request.POST.get("amount")),
                amount_type=amount_type,
                price=price,
                confirmed_price=confirmed_price,
                price_type=price_type,
                import_comment=request.POST.get("import_comment"),
                is_active="active",
            )

        MaterialStorageHistory.objects.create(
            executor=request.user,
            material=material_type,
            action="import",
            amount=int(request.POST.get("amount")),
            price=price,
            price_type=price_type,
            amount_type=amount_type,
            where="material",
        )

    @classmethod
    def accept_material(cls, request, material):
        MaterialStorageHistory.objects.create(
            executor=request.user,
            material=material.material,
            action="confirm",
            amount=material.amount,
            price=material.price,
            price_type=material.price_type,
            amount_type=material.amount_type,
            where="material",
        )

    @classmethod
    def cancel_material(cls, request, material):
        MaterialStorageHistory.objects.create(
            executor=request.user,
            material=material.material,
            action="cancel",
            amount=material.amount,
            price=material.price,
            price_type=material.price_type,
            amount_type=material.amount_type,
            where="material",
        )


# SPARE TYPES, STORAGE AND HISTORY
class SpareType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class SpareStorage(models.Model):
    spare = models.ForeignKey(
        SpareType, on_delete=models.PROTECT, verbose_name="Ehtiyot qism"
    )
    amount = models.CharField(max_length=255, verbose_name="Miqdori")
    amount_type = models.CharField(
        max_length=16, choices=AMOUNTS, default="meter", verbose_name="Miqdor turi"
    )

    price = models.CharField(max_length=600, default=0, verbose_name="Narxi")
    confirmed_price = models.CharField(
        max_length=600, default=0, verbose_name="Tasdiqlangan narxi"
    )

    price_type = models.CharField(
        choices=CURRENCIES, default="usd", max_length=3, verbose_name="Pul birligi"
    )

    is_active = models.CharField(
        choices=ACTIVE, default="active", max_length=8, verbose_name="Holati"
    )

    import_comment = models.CharField(max_length=255, verbose_name="Izoh")

    barcode = models.CharField(max_length=255, verbose_name="Barkod")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Oxirgi yangilanish")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Qo'shilgan vaqti"
    )

    def __str__(self) -> str:
        return self.spare.name

    @classmethod
    def import_spare(cls, request):
        spare_id = request.POST.get("spare")
        price = request.POST.get("price")
        confirmed_price = request.POST.get("confirmed_price")
        price_type = request.POST.get("price_type")
        amount_type = request.POST.get("amount_type")
        barcode = request.POST.get("barcode")

        spare_type = SpareType.objects.get(id=spare_id)

        spare = cls.objects.filter(
            spare=spare_type,
            price=price,
            confirmed_price=confirmed_price,
            price_type=price_type,
            amount_type=amount_type,
            barcode=barcode,
            is_active="active",
        )

        if spare.exists():
            m = spare.first()
            m.amount = float(m.amount) + float(request.POST.get("amount"))
            m.import_comment = request.POST.get("import_comment")
            m.save()

        else:
            cls.objects.create(
                spare=spare_type,
                amount=float(request.POST.get("amount")),
                amount_type=amount_type,
                price=price,
                confirmed_price=confirmed_price,
                price_type=price_type,
                import_comment=request.POST.get("import_comment"),
                barcode=barcode,
                is_active="active",
            )

        SpareStorageHistory.objects.create(
            executor=request.user,
            spare=spare_type,
            action="import",
            amount=int(request.POST.get("amount")),
            price=price,
            price_type=price_type,
            amount_type=amount_type,
            where="spare",
        )

    def export(self, user, amount, where):
        SpareStorageHistory.objects.create(
            executor=user,
            spare=self.spare,
            action="export",
            amount=amount,
            amount_type=self.amount_type,
            price=self.price,
            price_type=self.price_type,
            where=where,
        )

        self.amount = float(self.amount) - float(amount)
        self.save()

        if float(self.amount) <= 0:
            self.delete()


class SpareStorageHistory(models.Model):
    executor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    spare = models.ForeignKey(SpareType, on_delete=models.SET_NULL, null=True)

    action = models.CharField(choices=ACTION_TYPES, max_length=9)
    amount = models.CharField(default="0", max_length=255)
    amount_type = models.CharField(choices=AMOUNTS, max_length=5, default="meter")
    price = models.CharField(max_length=255, blank=True)
    price_type = models.CharField(choices=CURRENCIES, default="usd", max_length=5)
    where = models.CharField(choices=WHERE, max_length=16, default="null")

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


# LABEL TYPES, STORAGE AND HISTORY
class LabelType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class LabelStorage(models.Model):
    label = models.ForeignKey(
        LabelType, on_delete=models.PROTECT, verbose_name="Etiketika turi"
    )
    amount = models.IntegerField(default=0, verbose_name="Miqdori")
    amount_type = models.CharField(
        choices=AMOUNTS, max_length=5, default="point", verbose_name="Miqdor turi"
    )
    price = models.CharField(max_length=255, verbose_name="Narxi")
    confirmed_price = models.CharField(
        max_length=600, default=0, verbose_name="Tasdiqlangan narxi"
    )

    price_type = models.CharField(
        choices=CURRENCIES, default="usd", max_length=3, verbose_name="Pul birligi"
    )

    import_comment = models.CharField(max_length=255, verbose_name="Izoh")

    is_active = models.CharField(
        choices=ACTIVE, max_length=8, default="active", verbose_name="Aktiv"
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label.name

    @classmethod
    def import_label(cls, request):
        label_id = request.POST.get("label")
        price = request.POST.get("price")
        confirmed_price = request.POST.get("confirmed_price")
        price_type = request.POST.get("price_type")
        amount_type = request.POST.get("amount_type")

        label_type = LabelType.objects.get(id=label_id)

        label = cls.objects.filter(
            label=label_type,
            price=price,
            confirmed_price=confirmed_price,
            price_type=price_type,
            amount_type=amount_type,
            is_active="active",
        )

        if label.exists():
            m = label.first()
            m.amount = float(m.amount) + float(request.POST.get("amount"))
            m.import_comment = request.POST.get("import_comment")
            m.save()

        else:
            cls.objects.create(
                label=label_type,
                amount=float(request.POST.get("amount")),
                amount_type=amount_type,
                price=price,
                confirmed_price=confirmed_price,
                price_type=price_type,
                import_comment=request.POST.get("import_comment"),
                is_active="active",
            )

        LabelStorageHistory.objects.create(
            executor=request.user,
            label=label_type,
            action="import",
            amount=float(request.POST.get("amount")),
            price=price,
            price_type=price_type,
            amount_type=amount_type,
            where="label",
        )

    def export(self, user, amount, where):
        LabelStorageHistory.objects.create(
            executor=user,
            label=self.label,
            action="export",
            amount=amount,
            amount_type=self.amount_type,
            price=self.price,
            price_type=self.price_type,
            where=where,
        )

        self.amount = float(self.amount) - float(amount)
        self.save()

        if float(self.amount) <= 0:
            self.delete()


class LabelStorageHistory(models.Model):
    executor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    label = models.ForeignKey(LabelType, on_delete=models.SET_NULL, null=True)

    action = models.CharField(choices=ACTION_TYPES, max_length=9)
    amount = models.CharField(default="0", max_length=255)
    amount_type = models.CharField(choices=AMOUNTS, max_length=5, default="point")
    price = models.CharField(max_length=255, blank=True)
    price_type = models.CharField(choices=CURRENCIES, default="usd", max_length=5)
    where = models.CharField(choices=WHERE, max_length=16, default="null")

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Design(models.Model):
    SEX_TYPE = (
        ("male", "Erkak"),
        ("female", "Ayol"),
    )

    SEASON_TYPE = (
        ("winter", "Qishki"),
        ("summer", "Yozgi"),
    )

    name = models.CharField(max_length=255)
    amount = models.CharField(max_length=255, default=1)
    sex = models.CharField(max_length=10, choices=SEX_TYPE)
    season = models.CharField(max_length=6, choices=SEASON_TYPE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class DesignImmutable(models.Model):
    CALC_TYPES = (("percent", "Foiz"), ("sum", "So'm"))

    name = models.CharField(max_length=255)
    calc_type = models.CharField(max_length=255, choices=CALC_TYPES)
    cost = models.CharField(max_length=255)
    design = models.ForeignKey(Design, on_delete=models.CASCADE)
    task = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class DesignField(models.Model):
    material_type = models.ForeignKey(MaterialType, on_delete=models.CASCADE)
    design_type = models.ForeignKey(Design, on_delete=models.CASCADE)
    amount = models.CharField(max_length=255, default="0")

    def __str__(self):
        return self.material_type.name


class DesignLabel(models.Model):
    design = models.ForeignKey(Design, on_delete=models.CASCADE)
    label = models.ForeignKey(LabelType, on_delete=models.CASCADE)

    price = models.CharField(max_length=255, null=True, blank=True)


class ImmutableBalance(models.Model):
    CALC_TYPES = (("percent", "Foiz"), ("sum", "So'm"))
    type = models.CharField(max_length=255)
    calc_type = models.CharField(max_length=255, choices=CALC_TYPES)
    cost = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.type


class Exchange(models.Model):
    usd_currency = models.CharField(max_length=255, default=0)
    day = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.usd_currency
    
    
    
# PRODUCTION
class ProductionMaterialStorage(models.Model):
    material = models.ForeignKey(
        MaterialStorage, on_delete=models.PROTECT, null=True, blank=True)
    price = models.CharField(max_length=600, default=0)
    price_type = models.CharField(
        choices=CURRENCIES, default='usd', max_length=3)
    amount = models.CharField(max_length=255)
    is_active = models.CharField(
        choices=ACTIVE, default='pending', max_length=8)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ProductionMaterialStorageHistory(models.Model):
    executor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    production_material = models.ForeignKey(MaterialType, on_delete=models.SET_NULL, null=True)
    production_label = models.ForeignKey(LabelType, on_delete=models.SET_NULL, null=True)
    action = models.CharField(choices=ACTION_TYPES, max_length=9)
    amount = models.CharField(default="0", max_length=255)
    amount_type = models.CharField(choices=AMOUNTS, max_length=5, default="point")
    price = models.CharField(max_length=255, blank=True)
    price_type = models.CharField(choices=CURRENCIES, default="usd", max_length=5)
    where = models.CharField(choices=WHERE, max_length=16, default="null")

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Production(models.Model):
    design_type = models.ForeignKey(Design, on_delete=models.PROTECT)
    amount = models.CharField(max_length=255, default='0')
    price = models.CharField(max_length=255)
    comment = models.CharField(max_length=255, default="Izoh qoldiring")
    is_active = models.CharField(
        choices=ACTIVE, default='pending', max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.design_type.name


class ProductionHistory(models.Model):

    executor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    production = models.ForeignKey(Design, on_delete=models.SET_NULL, null=True)

    action = models.CharField(choices=ACTION_TYPES, max_length=15)
    amount = models.CharField(default="0", max_length=255)
    amount_type = models.CharField(choices=AMOUNTS, max_length=5, default="point")
    price = models.CharField(max_length=255, blank=True)
    price_type = models.CharField(choices=CURRENCIES, default="usd", max_length=5)
    where = models.CharField(choices=WHERE, max_length=16, default="null")

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Brak(models.Model):
    SORT_TYPES = (
        ('second', 'Ikkinchi sort'),
        ('third', 'Uchinchi sort')
    )

    STATUS_TYPES = (
        ('active', "Faol"),
        ('sold', "Sotilgan")
    )

    design = models.ForeignKey(
        Design, on_delete=models.PROTECT, null=True, blank=True)

    gr_amount = models.CharField(max_length=255, default=0)
    per_amount = models.CharField(max_length=255, default=0)

    status = models.CharField(max_length=20, choices=STATUS_TYPES)
    sort_type = models.CharField(choices=SORT_TYPES, max_length=15)
    date = models.DateTimeField(auto_now_add=True)


class ProductionWorker(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, blank=True, null=True)


class ProductionWorkerBalance(models.Model):
    worker = models.ForeignKey(ProductionWorker, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    amount = models.CharField(max_length=255)
    

class Expenditure(models.Model):
    executor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comment = models.CharField(max_length=400)
    cost = models.CharField(max_length=255)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    
class WorkerCredit(models.Model):
    amount = models.CharField(max_length=255)
    comment = models.CharField(max_length=255, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WorkerDebit(models.Model):
    amount = models.CharField(max_length=255)
    comment = models.CharField(max_length=255, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WorkerFine(models.Model):
    amount = models.CharField(max_length=255)
    comment = models.CharField(max_length=255, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WorkerWork(models.Model):
    amount = models.CharField(max_length=255)
    cost = models.CharField(max_length=255, default=0)
    comment = models.CharField(max_length=255, null=True, blank=True)


    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Worker(models.Model):
    SALARY_TYPES = (
        ('daily', 'Donabay'),
        ('monthly', 'Oylik'),
        ('per_way', 'Aravabay')
    )

    JOB_TYPES = (
        ('administration', 'Mamuriyat'),
        ('master', 'Usta'),
        ('tailor', 'Tikuvchi'),
        ('rosso_tailor', 'Rosso tikuvchisi'),
        ('turner', 'Ag`daruvchi'),
        ('moulder', 'Qolipchi'),
        ('charioteer', 'Arava yechuvchi'),
        ('taster', 'Tahlovchi'),
        ('label_setter', 'Etiketika uruvchi'),
        ('packer', 'Qadoqchi'),
    )

    name = models.CharField(max_length=255)
    job_type = models.CharField(choices=JOB_TYPES, max_length=20)
    phone = models.CharField(max_length=255, null=True, blank=True)
    salary = models.CharField(max_length=255, default=0)
    salary_types = models.CharField(choices=SALARY_TYPES, max_length=15)

    address = models.CharField(max_length=255, null=True, blank=True)
    car_number = models.CharField(max_length=255, null=True, blank=True)
    driver = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class WorkerAccount(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.PROTECT)

    credits = models.CharField(max_length=255, default=0)
    credits_history = models.ManyToManyField(
        WorkerCredit, null=True, blank=True)

    debits = models.CharField(max_length=255, default=0)
    debits_history = models.ManyToManyField(WorkerDebit, null=True, blank=True)

    fines = models.CharField(max_length=255, default=0)
    fines_history = models.ManyToManyField(WorkerFine, null=True, blank=True)

    workerworks_cost = models.CharField(max_length=255, default=0)
    workerworks_history = models.ManyToManyField(
        WorkerWork, null=True, blank=True)
    
    completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    
    
class Product(models.Model):
    ACTIVE = (
        ('active', 'Faol'),
        ('inactive', 'Nofaol'),
        ('pending', 'Kutilmoqda')
    )
    design_type = models.ForeignKey(Design, on_delete=models.PROTECT)
    amount = models.CharField(max_length=255, default='0')
    price = models.CharField(max_length=255)
    comment = models.CharField(max_length=255, default="Izoh qoldiring")
    is_active = models.CharField(
        choices=ACTIVE, default='pending', max_length=8)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.design_type.name


class ProductHistory(models.Model):
    executor = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, default="O'chirilgan foydalanuvchi")
    action = models.CharField(choices=ACTION_TYPES, max_length=7)
    details = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
