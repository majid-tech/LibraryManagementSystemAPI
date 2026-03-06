from django.contrib import admin
from django.urls import path, include  # 1. Import include
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('library_api.urls')),  # 2. Route all 'api/' paths to your app
]
