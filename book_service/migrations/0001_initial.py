# Generated by Django 4.2.3 on 2023-07-27 09:51

import book_service.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
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
                ("title", models.CharField(max_length=255)),
                ("author", models.CharField(max_length=255)),
                (
                    "cover",
                    models.ImageField(
                        null=True, upload_to=book_service.models.movie_image_file_path
                    ),
                ),
                (
                    "inventory",
                    models.IntegerField(
                        default=0,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("daily_fee", models.DecimalField(decimal_places=2, max_digits=5)),
            ],
            options={
                "verbose_name": "book",
                "verbose_name_plural": "books",
            },
        ),
    ]
