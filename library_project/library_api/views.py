from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Book, BorrowRecord
from .serializers import BookSerializer, BorrowRecordSerializer, RegisterSerializer

# --- Authentication Views ---
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

# --- Book Views ---
class BookList(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

# --- Borrowing Logic ---
class BorrowBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        
        if book.available_copies > 0:
            book.available_copies -= 1
            book.save()
            
            record = BorrowRecord.objects.create(
                user=request.user,
                book=book,
                is_returned=False
            )
            return Response(BorrowRecordSerializer(record).data, status=status.HTTP_201_CREATED)
        
        return Response({"error": "No copies available"}, status=status.HTTP_400_BAD_REQUEST)

class ReturnBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, record_id):
        record = get_object_or_404(BorrowRecord, id=record_id, user=request.user, is_returned=False)
        
        record.is_returned = True
        record.save()
        
        book = record.book
        book.available_copies += 1
        book.save()
        
        return Response({"message": "Book returned successfully"}, status=status.HTTP_200_OK)
