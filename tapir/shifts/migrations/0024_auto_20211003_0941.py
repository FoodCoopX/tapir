# Generated by Django 3.1.13 on 2021-10-03 07:41

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("shifts", "0023_auto_20210923_2152"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShiftExemption",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start_date", models.DateField(verbose_name="Start date")),
                ("end_date", models.DateField(verbose_name="End date")),
                ("description", models.TextField(verbose_name="Description")),
                (
                    "shift_user_data",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shift_exemptions",
                        to="shifts.shiftuserdata",
                    ),
                ),
            ],
        ),
    ]
