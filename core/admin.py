from django.contrib import admin
from .models import FarmerProfile, SupplierProfile, Product, Order


# ===============================
# Farmer Profile Admin
# ===============================
@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'full_name',
        'phone',
        'location',
        'farm_size',
        'created_at',
    )
    search_fields = (
        'full_name',
        'user__username',
        'phone',
        'location',
    )
    list_filter = ('location',)
    ordering = ('-created_at',)


# ===============================
# Supplier Profile Admin
# ===============================
@admin.register(SupplierProfile)
class SupplierProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'company_name',
        'phone',
        'location',
    )
    search_fields = (
        'company_name',
        'user__username',
        'phone',
        'location',
    )
    list_filter = ('location',)


# ===============================
# Product Admin
# ===============================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'supplier',
        'price',
        'stock',
    )
    search_fields = (
        'name',
        'supplier__company_name',
        'supplier__user__username',
    )
    list_filter = ('supplier',)


# ===============================
# Order Admin
# ===============================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'farmer',
        'supplier',
        'product',
        'quantity',
        'status',
        'created_at',
    )

    search_fields = (
        'farmer__user__username',
        'supplier__user__username',
        'product__name',
    )

    list_filter = ('status', 'created_at')
