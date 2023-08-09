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
            "borrowing_date",
            "expected_return_date",
            "actual_return_date"
        )
        read_only_fields = ("id", "user")


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "user",
            "book",
            "borrowing_date",
            "expected_return_date",
            "actual_return_date"
        )
        read_only_fields = (
            "id",
            "user",
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
            "book",
            "user"
        )

    @transaction.atomic
    def create(self, validated_data):
        book_instance = validated_data["book"]
        book_instance.inventory -= 1
        book_instance.save()
        borrowing = Borrowing.objects.create(**validated_data)
        message = (
            f"Dear User {borrowing.user.email} "
            f"you borrow a book: Book {borrowing.book.title}, "
            f"date: {borrowing.borrowing_date}")
        send_to_telegram(message)

        return borrowing

    def validate_book(self, attrs):
        data = self.book.validate(attrs=attrs)
        if data.inventory == 0:
            raise serializers.ValidationError(
                f"There is no {data.title} books left"
            )
        return data


class ReturnBorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")
        read_only_fields = ("id", "actual_return_date")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs.get("actual_return_date") is not None:
            raise serializers.ValidationError(
                "Borrowing already returned"
            )
        return attrs

    def update(self, instance, validated_data):
        instance.actual_return_date = date.today()
        instance.save()
        return instance
