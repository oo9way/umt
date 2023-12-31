from django import forms
from materials.models import (
    Design,
    DesignField,
    DesignImmutable,
    Expenditure,
    ImmutableBalance,
    LabelStorage,
    LabelType,
    MaterialStorage,
    MaterialType,
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
        fields = "__all__"
        labels = {
            "name": "Nomi",
            "materials": "Material turi",
            "label": "Etiketika turi",
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