# Generated by Django 4.2.16 on 2024-10-16 19:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Ahmet",
            fields=[
                ("version", models.BigAutoField(primary_key=True, serialize=False)),
                ("event", models.CharField(max_length=256)),
                ("event_date", models.DateField(auto_now=True)),
                ("rate", models.DecimalField(decimal_places=2, max_digits=10)),
                ("data", models.JSONField()),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Burak",
            fields=[
                ("version", models.UUIDField(primary_key=True, serialize=False)),
                ("event", models.CharField(max_length=256)),
                ("data", models.JSONField()),
                ("is_active", models.BooleanField(default=True)),
                (
                    "parent",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="buraks",
                        to="bulk_test.ahmet",
                    ),
                ),
            ],
        ),
    ]
