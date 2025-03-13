from django.contrib import admin
from .models import Category, Product, NavbarLink
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')

# Only register User if it's not already registered
try:
    admin.site.register(User, UserAdmin)
except admin.sites.AlreadyRegistered:
    pass  # Ignore if already registered

admin.site.register(NavbarLink)
