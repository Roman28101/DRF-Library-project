from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAdminUser, \
    IsAuthenticated

from borrowing_service.models import Borrowing
from borrowing_service.serializers import \
    BorrowingSerializer, BorrowingDetailSerializer


class BorrowingDetailAPIView(
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
        serializer.save(user=self.request.user)