from django.contrib import admin

from app.core.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
