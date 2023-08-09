import os
import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


def book_cover_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads", "books", filename)


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.ImageField(null=True, upload_to=book_cover_file_path, blank=True)
    inventory = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = "book"
        verbose_name_plural = "books"

    def __str__(self):
        return f"{self.title} {self.author}"
