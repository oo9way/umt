# Generated by Django 4.2 on 2024-01-03 19:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0048_rename_labels_design_materials'),
    ]

    operations = [
        migrations.RenameField(
            model_name='designpricehistory',
            old_name='labels',
            new_name='materials',
        ),
    ]