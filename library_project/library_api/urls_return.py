from django.urls import path

from .views import ReturnView

urlpatterns = [
    path("", ReturnView.as_view(), name="return"),
]
