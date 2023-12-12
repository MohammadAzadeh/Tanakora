from rest_framework import serializers
from .models import Order, OrderItem, Coupon




class CartItemAddSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()

class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['code']