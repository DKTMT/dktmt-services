# Generated by Django 4.1.5 on 2023-02-14 03:55

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Portfolio",
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
                ("hashed_email", models.CharField(max_length=255)),
                ("exchange", models.CharField(max_length=64)),
                ("port_value", models.FloatField()),
                ("coins_possess", models.JSONField()),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
