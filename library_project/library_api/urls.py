from django.urls import path
from .views import RegisterView, BookList, BorrowBookView, ReturnBookView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('books/', BookList.as_view(), name='book-list'),
    path('borrow/<int:book_id>/', BorrowBookView.as_view(), name='borrow-book'),
    path('return/<int:record_id>/', ReturnBookView.as_view(), name='return-book'),
]
