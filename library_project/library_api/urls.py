from django.urls import include, path

urlpatterns = [
    path("auth/", include("library_api.urls_auth")),
    path("books/", include("library_api.urls_books")),
    path("users/", include("library_api.urls_users")),
    path("borrow/", include("library_api.urls_borrow")),
    path("return/", include("library_api.urls_return")),
    path("my-borrows/", include("library_api.urls_my_borrows")),
]
