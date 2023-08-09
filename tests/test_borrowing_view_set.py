from datetime import date, timedelta
from unittest.mock import patch

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book_service.models import Book
from book_service.serializers import BookSerializer
from borrowing_service.models import Borrowing
from borrowing_service.serializers import BorrowingListSerializer
from borrowing_service.tasks import check_overdue_borrowings

BORROWING_URL = reverse("borrowing_service:borrowing-list")


def some_book(**params):
    defaults = {
        "title": "IT",
        "author": "Stephen King",
        "inventory": 10,
        "daily_fee": 0.15
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def detail_url(borrowing_id: int):
    return reverse("borrowing_service:borrowing-detail", args=[borrowing_id])


class UnauthenticatedBorrowingTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@test.com",
            "user1234",
        )
        self.client.force_authenticate(self.user)
        self.book1 = some_book()
        self.book2 = some_book(title="LOTR")
        self.serializer = BookSerializer(self.book1)
        self.borrowing = Borrowing.objects.create(
            book=self.book1,
            user=self.user
        )
        self.borrowing2 = Borrowing.objects.create(
            book=self.book2,
            user=self.user,
            actual_return_date=date.today(),
        )

    def test_list_borrowings(self):
        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.filter(user=self.user)
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_borrowings_authenticated(self):
        response = self.client.get(detail_url(self.borrowing.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AdminPlayTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "admin1234",
            is_staff=True,
        )

        self.client.force_authenticate(self.user)
        self.book1 = some_book()
        self.book2 = some_book(title="Winnie The Pooh")
        self.serializer1 = BookSerializer(self.book1)
        self.serializer2 = BookSerializer(self.book2)
        self.borrowing1 = Borrowing.objects.create(
            book=self.book1,
            user=self.user
        )
        self.borrowing2 = Borrowing.objects.create(
            book=self.book2,
            user=self.user,
            actual_return_date=date.today(),
        )

    def test_borrowings_filter(self):
        self.client.force_authenticate(self.user)
        res_user = self.client.get(
            BORROWING_URL,
            {"user_id": f"{self.user.id}"}
        )

        res_user_is_active = self.client.get(
            BORROWING_URL,
            {"user_id": f"{self.user.id}"},
            {"is_active": f"True"}
        )

        serializer1 = BorrowingListSerializer(self.borrowing1)
        serializer2 = BorrowingListSerializer(self.borrowing2)


        self.assertIn(serializer1.data, res_user.data)
        self.assertIn(serializer1.data, res_user_is_active.data)
        self.assertIn(serializer2.data, res_user_is_active.data)


class CheckOverdueBorrowingsTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@user.com",
            password="testpassword"
        )
        self.book = Book.objects.create(
            title="The Witcher",
            author="Andrzej Sapkowski",
            daily_fee=0.6
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date() - timedelta(days=1)
        )

    @patch("borrowing_service.tasks.send_to_telegram")
    def test_check_overdue_borrowings(self, mock_send_to_telegram):
        check_overdue_borrowings()

        mock_send_to_telegram.assert_called_with(
            f"Overdue borrowing: Book {self.borrowing.book.title} borrowed by {self.borrowing.user.email}"
        )
