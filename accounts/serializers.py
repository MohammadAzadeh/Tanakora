from rest_framework import serializers
from .models import User, Product, Wallet, Transaction, OtpCode


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        #extra_kwargs = {
        #    'password': {'write_only': True}
        #    }

    def create(self, validated_data):
        del validated_data['password2']
        return User.objects.create_user(**validated_data)

    def validate_username(self, value):
        if value == 'admin':
            raise serializers.ValidationError('username cant be admin')
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('passwords must match')
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'biography', 'profile', 'logo', 'instagram', 'youtube', 'twitter', 'facebook', 'linkedin']

class UserProfileEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'firstname', 'lastname', 'biography', 'profile', 'logo', 'instagram', 'youtube', 'twitter', 'facebook', 'linkedin']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'color', 'price', 'image', 'description', 'is_available', 'quantity']

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance']

class TransactionPanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['count', 'status']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class LogoEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['logo']

class ProductAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

        def create(self, validated_data):
            product =  Product.objects.create(**validated_data)
            product.save()
            return product

class ProductEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'color', 'price', 'image', 'quantity', 'description', 'is_available']
            

class OtpCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtpCode
        fields = ['code']