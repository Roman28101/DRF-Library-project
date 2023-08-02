from datetime import date

from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, \
    IsAuthenticated
from rest_framework.response import Response

from borrowing_service.models import Borrowing
from borrowing_service.send_message_to_telegram import \
    send_to_telegram
from borrowing_service.serializers import \
    BorrowingSerializer, BorrowingDetailSerializer


class BorrowingAPIView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer
    permission_classes = (IsAdminUser, IsAuthenticated)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer

        return BorrowingSerializer

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        is_active = self.request.query_params.get("is_active", None)
        user_id = self.request.query_params.get("user_id", None)

        if user.is_stuff and user_id:
            queryset = queryset.filter(user_id=int(user_id))
        elif not user.is_staff:
            queryset = queryset.filter(user=user)
        if is_active:
            queryset = queryset.filter(actual_return_date__isnull=True)

        return queryset

    def perform_create(self, serializer):
        borrowing = serializer.save(user=self.request.user)
        message = (
            f"Dear User {borrowing.user.email} "
            f"you borrow a book: Book {borrowing.book.title}, "
            f"date: {borrowing.borrowing_date}")
        send_to_telegram(message)

    @action(
        methods=["GET"],
        detail=True,
        url_path="return",
        permission_classes=[IsAuthenticated]
    )
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()
        serializer = self.get_serializer(borrowing, data=request.data)
        if borrowing.actual_return_date is not None:
            return Response(
                {"detail": "Borrowing already returned"},
                status=status.HTTP_400_BAD_REQUEST
            )
        borrowing.actual_return_date = date.today()
        borrowing.book.inventory += 1
        borrowing.book.save()
        borrowing.save()
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)