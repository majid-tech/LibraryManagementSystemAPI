# Library Management System API

REST API for managing books and borrowing workflows, built with Django and Django REST Framework.

## Current Status

The project currently includes:

- Template-backed project landing page at `/`
- User registration and token authentication
- Book management with admin write access
- Borrow checkout and return flows with transaction safety
- Per-user borrow history endpoint
- Filtering, search, and ordering on books
- URL structure organized by feature area

## Tech Stack

- Python 3.13
- Django 5.1.5
- Django REST Framework
- django-filter
- SQLite (default dev database)

## Project Structure

```text
library_project/
  manage.py
  db.sqlite3
  library_project/
    settings.py
    urls.py
  library_api/
    models.py
    serializers.py
    views.py
    permissions.py
    urls.py
    urls_auth.py
    urls_books.py
    urls_users.py
    urls_borrow.py
    urls_return.py
    urls_my_borrows.py
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install Django==5.1.5 djangorestframework django-filter
```

3. Run migrations:

```bash
cd library_project
python manage.py migrate
```

4. Start server:

```bash
python manage.py runserver
```

Base API URL:

```text
http://127.0.0.1:8000/api/
```

Project landing page:

```text
http://127.0.0.1:8000/
```

## Authentication

### Register

- `POST /api/auth/register/`
- Body:

```json
{
  "username": "john",
  "email": "john@example.com",
  "password": "StrongPassword123!"
}
```

### Get Token

- `POST /api/auth/token/`
- Body:

```json
{
  "username": "john",
  "password": "StrongPassword123!"
}
```

Use returned token in protected requests:

```text
Authorization: Token <your_token>
```

## API Endpoints

### Books

- `GET /api/books/` list books
- `GET /api/books/{id}/` retrieve book
- `POST /api/books/` create book (admin)
- `PUT/PATCH /api/books/{id}/` update book (admin)
- `DELETE /api/books/{id}/` delete book (admin)

Supported book query params:

- `available=true` only books with `available_copies > 0`
- `author=<author_name>` filter by author
- `search=<title_term>` search by title
- `ordering=title|author|available_copies|created_at`

### Users (Admin only)

- `GET /api/users/`
- `GET /api/users/{id}/`
- `POST /api/users/`
- `PUT/PATCH /api/users/{id}/`
- `DELETE /api/users/{id}/`

### Borrowing

- `POST /api/borrow/checkout/` (authenticated)
- Body:

```json
{
  "book_id": 1
}
```

- `GET /api/borrow/records/` (admin)
- `GET /api/borrow/records/{id}/` (admin)
- `POST /api/borrow/records/` (admin)
- `PUT/PATCH /api/borrow/records/{id}/` (admin)
- `DELETE /api/borrow/records/{id}/` (admin)

### Return

- `POST /api/return/` (authenticated borrower or admin)
- Body:

```json
{
  "record_id": 4
}
```

### My Borrows

- `GET /api/my-borrows/` (authenticated)

## Permission Matrix

- Books:
  - `list/retrieve`: public
  - `create/update/delete`: admin only
- Users: admin only
- Borrow records resource endpoints: admin only
- Checkout: authenticated users
- Return: authenticated + owner of record (or admin)
- My borrows: authenticated users

## Borrowing Business Rules

### Checkout

- Must be authenticated
- Book must exist
- `available_copies` must be greater than 0
- User cannot have another active borrow for same book
- Performed in atomic transaction:
  - lock book row
  - decrement `available_copies`
  - create borrow record

### Return

- Must be authenticated
- Borrow record must exist
- Caller must own the record (or be admin)
- Record must not already be returned
- Performed in atomic transaction:
  - lock borrow record and book row
  - mark record returned
  - set `return_date`
  - increment `available_copies`

## Data Models

### Book

- `title`
- `author`
- `isbn` (unique)
- `total_copies`
- `available_copies`
- timestamps

### BorrowRecord

- `user`
- `book`
- `borrow_date`
- `due_date` (nullable)
- `return_date` (nullable)
- `is_returned`


## Useful Commands

```bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
