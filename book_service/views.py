from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response

from book_service.models import Book
from book_service.serializers import BookSerializer, BookCoverSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == "upload_cover":
            return BookCoverSerializer

        return BookSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-cover",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        book = self.get_object()
        serializer = self.get_serializer(book, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
