from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing_service.models import Borrowing
from borrowing_service.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    ReturnBorrowingSerializer,
    BorrowingListSerializer
)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "return_borrowing":
            return ReturnBorrowingSerializer

        return BorrowingSerializer

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        user_id = self.request.query_params.get("user_id", None)
        is_active = self.request.query_params.get("is_active", None)

        if user.is_staff and user_id:
            queryset = queryset.filter(user__id=int(user_id))
        elif not user.is_staff:
            queryset = queryset.filter(user=user)
        if is_active is not None:
            is_active = bool(is_active.lower() == "true")
            queryset = queryset.filter(
                Q(actual_return_date__isnull=True) if is_active else
                Q(actual_return_date__isnull=False)
            )

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="user",
                type={"type": "number"},
                description="Filter by user id (ex. ?user=1), "
                            "or all users (ex. ?user)",
            ),
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.BOOL,
                description="Filter by borrowing status"
                            "(use ?is_active=true is you want to filter by active borrowings, "
                            "if you want to see returned borrowings use ?is_active=false)",
                required=False
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
        permission_classes=[IsAuthenticated]
    )
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()
        serializer = self.get_serializer(borrowing, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
