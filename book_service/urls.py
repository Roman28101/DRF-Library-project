from django.urls import include
from rest_framework import routers

from book_service.views import BookViewSet

router = routers.DefaultRouter()
router.register("books", BookViewSet)

urlpatterns = include(router.urls)

app_name = "book_service"
