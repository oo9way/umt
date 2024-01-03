from django import forms
from materials.models import (
    Design,
    DesignField,
    DesignImmutable,
    Expenditure,
    Finance,
    ImmutableBalance,
    LabelStorage,
    LabelType,
    MaterialStorage,
    MaterialType,
    ProductStock,
    SpareStorage,
    SpareType,
    Worker,
)
from user.models import User


class InsertMaterialForm(forms.ModelForm):
    class Meta:
        model = MaterialStorage
        fields = (
            "material",
            "amount",
            "amount_type",
            "price",
            "confirmed_price",
            "price_type",
            "import_comment",
        )

        labels = {
            "material": "Homashyo",
            "amount": "Miqdor",
            "amount_type": "Miqdor turi",
            "price": "Narx",
            "confirmed_price": "Tasdiqlangan narx",
            "price_type": "Pul birligi",
            "import_comment": "Izoh",
        }


class InsertMaterialTypeForm(forms.ModelForm):
    class Meta:
        model = MaterialType
        fields = ("name",)
        labels = {"name": "Homashyo nomi"}


class InsertSpare(forms.ModelForm):
    class Meta:
        model = SpareStorage
        fields = (
            "spare",
            "amount",
            "amount_type",
            "price",
            "confirmed_price",
            "price_type",
            "import_comment",
            "barcode",
        )


class InsertSpareTypeForm(forms.ModelForm):
    class Meta:
        model = SpareType
        fields = ("name",)
        labels = {"name": "Ehtiyot qism nomi"}


class InsertLabel(forms.ModelForm):
    class Meta:
        model = LabelStorage
        fields = (
            "label",
            "amount",
            "amount_type",
            "price",
            "confirmed_price",
            "price_type",
            "import_comment",
        )


class InsertLabelTypeForm(forms.ModelForm):
    class Meta:
        model = LabelType
        fields = ("name",)
        labels = {"name": "Etiketika nomi"}


class AdminDesign(forms.ModelForm):
    class Meta:
        model = Design
        fields = ("name", "amount", "sex", "season",)
        labels = {
            "name": "Nomi",
            "amount": "Juft miqdori",
            "sex": "Jinsi",
            "season": "Mavsumi",
        }


class AdminDesignFieldForm(forms.ModelForm):
    class Meta:
        model = DesignField
        fields = "__all__"
        labels = {"material_type": "Homashyo turi", "amount": "Miqdori"}


InlineDesignField = forms.models.inlineformset_factory(
    Design,
    DesignField,
    labels={"material_type": "Homashyo turi", "amount": "Miqdori"},
    fields=("material_type", "amount"),
    extra=12,
)


class AdminImmutables(forms.ModelForm):
    class Meta:
        model = DesignImmutable
        fields = "__all__"
        exclude = ["design"]
        labels = {"name": "Nomi", "calc_type": "Hisoblash turi", "cost": "Qiymat"}


class AdminAllImmutables(forms.ModelForm):
    class Meta:
        model = ImmutableBalance
        fields = "__all__"
        exclude = ["design"]
        labels = {
            "type": "Nomi",
            "cost": "Qiymat",
            "calc_type": "Hisoblash turi",
        }


class ImportMaterialToProduction(forms.Form):
    material = forms.ModelChoiceField(
        queryset=MaterialStorage.objects.all(),
        label='Homashyo',
    )
    amount = forms.IntegerField(label='Miqdori')
    
    
class SellBrak(forms.Form):
    price = forms.IntegerField(label='Narxi', required=True)
    

class ExpenditureForm(forms.ModelForm):
    class Meta:
        model = Expenditure
        fields = ("comment", "cost")
        labels = {
            "comment":"Izoh",
            "cost":"Summa"
        }
        
        
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "password", "role",)
        labels = {
            "username":"Login",
            "password":"Parol",
            "role":"Status"
        }
        
class AdminWorker(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ['name', 'phone', 'job_type', 'salary', 'salary_types', 'address', 'car_number', 'driver']
        exclude = ['credits', 'debits', 'fines', 'workerworks']

        labels = {
            'name': "F.I.O",
            'phone': "Telefon raqam",
            'job_type': "Ish turi",
            'salary': "Maosh miqdori",
            "salary_types": "Maosh turi",
            "address": "Manzil",
            "car_number": "Mashina raqami",
            "driver": "Haydovchi"
        }
        
        
class FinanceForm(forms.ModelForm):
    class Meta:
        model = Finance
        fields = ('cost', 'price_type', 'comment', 'type',)
        
        
class AdminProductStockForm(forms.ModelForm):
    class Meta:
        model = ProductStock
        fields = ['set_amount', 'product_per_set',
                  'comment', 'confirmed_price']
        labels = {
            'set_amount': "Qop soni",
            'product_per_set': 'Qopdagi mahsulot soni',
            'confirmed_price': 'Tasdiqlangan narxi',
            'comment': "Izoh"
        }

    def __init__(self, *args, **kwargs):
        super(AdminProductStockForm, self).__init__(*args, **kwargs)
        self.visible_fields()[3].field.widget.attrs['class'] = 'mb-0'