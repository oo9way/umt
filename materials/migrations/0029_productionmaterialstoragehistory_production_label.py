# Generated by Django 5.0 on 2023-12-29 02:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0028_alter_productionmaterialstoragehistory_production_material'),
    ]

    operations = [
        migrations.AddField(
            model_name='productionmaterialstoragehistory',
            name='production_label',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='materials.labeltype'),
        ),
    ]
