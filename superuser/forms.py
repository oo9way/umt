from django import forms
from materials.models import (
    LabelStorage,
    LabelType,
    MaterialStorage,
    MaterialType,
    SpareStorage,
    SpareType,
)


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
