from django.urls import include
from rest_framework import routers


from borrowing_service.views import BorrowingAPIView

router = routers.DefaultRouter()
router.register("borrowings", BorrowingAPIView)

urlpatterns = include(router.urls)

app_name = "borrowing_service"
