# Generated by Django 4.2 on 2024-01-03 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0045_alter_productstock_price_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='design',
            name='sex',
            field=models.CharField(choices=[('male', 'Erkak'), ('female', 'Ayol'), ('young', "O'smir"), ('baby', 'Bola')], max_length=10),
        ),
    ]