from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Book, BorrowRecord

# 1. User Serializer (Basic info)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# 2. Register Serializer (Custom for account creation)
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user

# 3. Book Serializer
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'total_copies', 'available_copies']

# 4. BorrowRecord Serializer
class BorrowRecordSerializer(serializers.ModelSerializer):
    # Nesting BookSerializer for GET requests, but using ID for POST
    book_details = BookSerializer(source='book', read_only=True)
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = BorrowRecord
        fields = [
            'id', 'user', 'user_details', 'book', 'book_details', 
            'borrow_date', 'due_date', 'return_date', 'is_returned'
        ]
        extra_kwargs = {
            'user': {'write_only': True},
            'book': {'write_only': True}
        }
