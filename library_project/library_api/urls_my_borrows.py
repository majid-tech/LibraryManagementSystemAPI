from django.urls import path

from .views import MyBorrowsView

urlpatterns = [
    path("", MyBorrowsView.as_view(), name="my-borrows"),
]
