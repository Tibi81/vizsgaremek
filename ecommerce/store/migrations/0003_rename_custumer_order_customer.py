# Generated by Django 5.1.1 on 2024-09-22 13:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_product_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='custumer',
            new_name='customer',
        ),
    ]