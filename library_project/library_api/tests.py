from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class ProjectSmokeTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_home_page_renders_template(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Library Management System API")

    def test_books_list_is_public(self):
        response = self.client.get("/api/books/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_my_borrows_requires_authentication(self):
        response = self.client.get("/api/my-borrows/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_my_borrows_with_token_returns_ok(self):
        user = User.objects.create_user(username="reader", password="StrongPass123!")
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.get("/api/my-borrows/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
