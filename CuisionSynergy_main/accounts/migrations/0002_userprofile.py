# Generated by Django 5.1.4 on 2024-12-08 05:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "profile_photo",
                    models.ImageField(
                        blank=True, null=True, upload_to="users/profile_pics"
                    ),
                ),
                (
                    "cover_photo",
                    models.ImageField(
                        blank=True, null=True, upload_to="users/cover_pics"
                    ),
                ),
                ("address_1", models.CharField(blank=True, max_length=50, null=True)),
                ("address_2", models.CharField(blank=True, max_length=50, null=True)),
                ("country", models.CharField(blank=True, max_length=20, null=True)),
                ("state", models.CharField(blank=True, max_length=15, null=True)),
                ("city", models.CharField(blank=True, max_length=10, null=True)),
                ("pincode", models.CharField(blank=True, max_length=6, null=True)),
                ("latitude", models.CharField(blank=True, max_length=20, null=True)),
                ("longitude", models.CharField(blank=True, max_length=20, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
