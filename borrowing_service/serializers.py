from django.db import transaction
from rest_framework import serializers

from book_service.serializers import BookSerializer
from borrowing_service.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "user",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date"
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(many=False, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrowing_date",
            "expected_return_date",
            "actual_return_date",
            "daily_fee",
            "book",
            "user"
        )

    def validate_book(self, attrs):
        data = self.book.validate(attrs=attrs)
        if data.inventory == 0:
            raise serializers.ValidationError(
                f"There is no {data.title} books left"
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        book_data = validated_data.pop("book")
        borrowing = Borrowing.objects.create(
            **book_data)

        return borrowing
