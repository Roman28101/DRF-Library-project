from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from book_service.models import Book


class Borrowing(models.Model):
    borrowing_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField(default=None, null=True, blank=True)
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )

    @staticmethod
    def validate_borrowing(borrowing_date, expected_return_date, error_to_raise):
        if (
                expected_return_date and borrowing_date
                and not (expected_return_date > borrowing_date)
        ):
            raise error_to_raise(
                "Expected return date must be not earlier than borrowing date"
            )

    def clean(self):
        Borrowing.validate_borrowing(
            self.borrowing_date,
            self.expected_return_date,
            ValidationError,
        )

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return super(Borrowing, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return str(self.borrowing_date)
