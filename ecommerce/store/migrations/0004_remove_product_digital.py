# Generated by Django 5.1.1 on 2024-09-28 07:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_rename_custumer_order_customer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='digital',
        ),
    ]
