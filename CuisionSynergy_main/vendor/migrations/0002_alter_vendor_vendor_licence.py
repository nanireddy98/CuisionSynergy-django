# Generated by Django 5.1.4 on 2024-12-09 15:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vendor", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vendor",
            name="vendor_licence",
            field=models.FileField(upload_to="vendor/license"),
        ),
    ]
