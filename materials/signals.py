from barcode import EAN13  # Adjust barcode type as needed
from io import BytesIO
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save
from django.dispatch import receiver
from materials.models import ProductStock
import random


def generate_random_number():
    return random.randint(100000000000, 999999999999)  # Inclusive range for 10 digits


def generate_barcode(instance):
    barcode_data = EAN13(str(generate_random_number()))  # Generate barcode based on model ID
    buffer = BytesIO()
    barcode_data.write(buffer)

    instance.barcode_image.save(
        f'barcode_{instance.id}.png',  # Customizable filename
        ContentFile(buffer.getvalue())
    )
    
    

@receiver(pre_save, sender=ProductStock)

def generate_barcode_pre_save(sender, instance, **kwargs):
    if not instance.barcode_image:  # Generate only if image is not set
        generate_barcode(instance)