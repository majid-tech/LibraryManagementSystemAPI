from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import BorrowRecordViewSet, CheckoutView

router = DefaultRouter()
router.register("records", BorrowRecordViewSet, basename="borrow-record")

urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name="checkout"),
]
urlpatterns += router.urls
