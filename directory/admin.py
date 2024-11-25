from django.contrib import admin
from .models import Branch, Product, GroupProduct


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(GroupProduct)
class GroupProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_group', 'unit')
    search_fields = ('name',)
    list_filter = ('product_group',)
    autocomplete_fields = ('product_group',)
