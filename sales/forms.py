from django.forms import ModelForm

from materials.models import ProductStock

class ProductStockForm(ModelForm):
    class Meta:
        model = ProductStock
        fields = ('design', 'set_amount', 'product_per_set', 'price', 'confirmed_price',  'comment')
        labels = {
            'design' : "Dizayn turi",
            'set_amount' : "Qop soni",
            'product_per_set' : "Qopdagi mahsulot soni",
            'price' : "Tannarxi",
            'confirmed_price' : "Tasdiqlangan narxi",
            'comment':"Izoh"
        }