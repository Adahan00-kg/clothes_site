# Generated by Django 5.1.3 on 2025-01-15 09:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_cartitem_cart'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clothes',
            name='clothes_photo',
        ),
    ]