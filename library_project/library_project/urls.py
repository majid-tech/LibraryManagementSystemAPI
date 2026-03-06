from django.contrib import admin
from django.urls import path, include  # 1. Import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('library_api.urls')),  # 2. Route all 'api/' paths to your app
]
