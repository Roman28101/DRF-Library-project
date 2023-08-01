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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)