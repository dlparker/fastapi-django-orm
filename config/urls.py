from django.contrib import admin
from django.urls import path

# Django is mounted under /d in app/main.py, so these are served at /d/...
urlpatterns = [
    path("admin/", admin.site.urls),
]
