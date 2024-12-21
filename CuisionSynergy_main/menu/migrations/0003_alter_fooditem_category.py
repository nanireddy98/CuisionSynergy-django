# Generated by Django 5.1.4 on 2024-12-20 16:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("menu", "0002_alter_category_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fooditem",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="fooditems",
                to="menu.category",
            ),
        ),
    ]
