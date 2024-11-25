from django.contrib import admin
from .models import Warehouse, ProductArrival, ProductStock, ProductExpense, Coming


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('branch', 'name')
    search_fields = ('name',)
    list_filter = ('branch',)
    autocomplete_fields = ('branch',)


@admin.register(Coming)
class ComingAdmin(admin.ModelAdmin):
    list_display = ('warehouse', 'contract_number', 'invoice_number')
    search_fields = ('warehouse', 'contract_number', 'invoice_number')
    list_filter = ('warehouse',)
    autocomplete_fields = ('warehouse',)


@admin.register(ProductArrival)
class ProductArrivalAdmin(admin.ModelAdmin):
    list_display = ('coming', 'product', 'quantity', 'unit_price', 'date', 'barcode')
    search_fields = ('product__name', 'warehouse__name', 'barcode')
    list_filter = ('coming', 'date')
    autocomplete_fields = ('coming', 'product')


@admin.register(ProductStock)
class ProductStockAdmin(admin.ModelAdmin):
    list_display = ('warehouse', 'product', 'quantity', 'barcode')
    list_filter = ('warehouse', 'product')
    search_fields = ('product__name', 'warehouse__name')
    autocomplete_fields = ('warehouse', 'product')


@admin.register(ProductExpense)
class ProductExpenseAdmin(admin.ModelAdmin):
    list_display = ('warehouse', 'product', 'quantity', 'unit_price', 'date')
    list_filter = ('warehouse', 'product')
    search_fields = ('product__name', 'warehouse__name')
    autocomplete_fields = ('warehouse', 'product')
