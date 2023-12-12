from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User, Wallet, Product, Transaction, Category, OtpCode

admin.site.unregister(Group)
admin.site.register(OtpCode)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'amount', 'shaba', 'created', 'status']
    list_filter = ['status']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_admin', 'is_influencer']
    list_filter = ['is_influencer']
    search_fields = ['username', 'email']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['name']
    search_fields = ['name']
    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'price','is_available']
    list_filter = ['is_available']
    search_fields = ['user', 'name']


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance']
    search_fields = ['user']


