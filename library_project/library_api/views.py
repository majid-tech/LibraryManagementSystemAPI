from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Book, BorrowRecord
from .permissions import IsBorrowerOrAdmin
from .serializers import (
    BookSerializer,
    BorrowRecordSerializer,
    RegisterSerializer,
    UserSerializer,
)

# Permission matrix:
# - BookViewSet:
#   - list/retrieve: AllowAny
#   - create/update/partial_update/destroy: IsAdminUser
# - UserViewSet:
#   - all actions: IsAdminUser
# - BorrowRecordViewSet:
#   - all actions: IsAdminUser
# - CheckoutView:
#   - post: IsAuthenticated
# - ReturnView:
#   - post: IsAuthenticated + IsBorrowerOrAdmin object check
# - MyBorrowsView:
#   - get: IsAuthenticated

# --- Authentication Views ---
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

# --- Resource ViewSets ---
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by("id")
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["author"]
    search_fields = ["title"]
    ordering_fields = ["title", "author", "available_copies", "created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        available = self.request.query_params.get("available")
        if available is not None and available.lower() in {"1", "true", "yes"}:
            queryset = queryset.filter(available_copies__gt=0)
        return queryset

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class BorrowRecordViewSet(viewsets.ModelViewSet):
    queryset = BorrowRecord.objects.select_related("user", "book").all().order_by("-borrow_date")
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsAdminUser]

# --- Borrowing Logic ---
class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        book_id = request.data.get("book_id")
        if not book_id:
            return Response(
                {"error": "book_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        book = get_object_or_404(Book.objects.select_for_update(), id=book_id)
        active_record_exists = BorrowRecord.objects.filter(
            user=request.user, book=book, is_returned=False
        ).exists()
        if active_record_exists:
            return Response(
                {"error": "You already have an active borrow for this book."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if book.available_copies <= 0:
            return Response(
                {"error": "No copies available."}, status=status.HTTP_400_BAD_REQUEST
            )

        book.available_copies -= 1
        book.save(update_fields=["available_copies", "updated_at"])

        record = BorrowRecord.objects.create(user=request.user, book=book, is_returned=False)
        return Response(BorrowRecordSerializer(record).data, status=status.HTTP_201_CREATED)


class ReturnView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        record_id = request.data.get("record_id")
        if not record_id:
            return Response(
                {"error": "record_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        record = get_object_or_404(
            BorrowRecord.objects.select_related("book").select_for_update(),
            id=record_id,
        )
        permission_check = IsBorrowerOrAdmin()
        if not permission_check.has_object_permission(request, self, record):
            return Response(
                {"error": "You do not have permission to return this record."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if record.is_returned:
            return Response(
                {"error": "This borrow record is already returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        book = Book.objects.select_for_update().get(id=record.book_id)
        record.is_returned = True
        record.return_date = timezone.now()
        record.save(update_fields=["is_returned", "return_date"])

        book.available_copies += 1
        book.save(update_fields=["available_copies", "updated_at"])

        return Response({"message": "Book returned successfully"}, status=status.HTTP_200_OK)


class MyBorrowsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        records = BorrowRecord.objects.select_related("book").filter(user=request.user).order_by(
            "-borrow_date"
        )
        serializer = BorrowRecordSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
