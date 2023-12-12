from django.contrib import admin
from .models import Order, OrderItem, Coupon

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'paid', 'updated']
    search_fields = ['user']
    list_filter = ['paid']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'price', 'quantity']
    search_fields = ['order', 'product']

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount', 'active', 'valid_from', 'valid_to']
    search_fields = ['code', 'discount']
    list_filter = ['active']

