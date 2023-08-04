from datetime import date

from django.db import transaction
from rest_framework import serializers

from book_service.serializers import BookSerializer
from borrowing_service.models import Borrowing
from borrowing_service.send_message_to_telegram import send_to_telegram


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
        book_data.inventory -= 1
        book_data.save()
        borrowing = Borrowing.objects.create(**book_data)
        message = (
            f"Dear User {borrowing.user.email} "
            f"you borrow a book: Book {borrowing.book.title}, "
            f"date: {borrowing.borrowing_date}")
        send_to_telegram(message)

        return borrowing


class ReturnBorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs.get("actual_return_date") is not None:
            raise serializers.ValidationError(
                "Borrowing already returned"
            )
        return attrs

    def create(self, validated_data):
        borrowing = super().create(validated_data)
        borrowing.return_date = date.today()
        borrowing.save()

        return borrowing
