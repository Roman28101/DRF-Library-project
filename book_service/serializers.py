from rest_framework import serializers

from book_service.models import Book


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ("id", "author", "cover", "inventory", "daily_fee")


class BookCoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "cover")
