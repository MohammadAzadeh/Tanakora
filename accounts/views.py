from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
import random
from .serializers import LogoEditSerializer, OtpCodeSerializer, ProductAddSerializer, ProductEditSerializer, UserRegisterSerializer, UserProfileSerializer, UserProfileEditSerializer, ProductSerializer, WalletSerializer, TransactionPanelSerializer, TransactionSerializer
from .models import User, Product, Wallet, Transaction, OtpCode
from permissions import IsOwnerOrReadOnly
from A.settings import EMAIL_HOST_USER


class UserRegister(APIView):
    def post(self, request):
        srz_data = UserRegisterSerializer(data=request.POST)
        if srz_data.is_valid():
            request.session['user_registration_info'] = dict(srz_data.data)
            random_code = random.randint(10000, 99999)
            OtpCode.objects.create(email=srz_data.data['email'], code=random_code)
            send_mail(subject='The authentication code', message=f'the code is {random_code}',from_email=EMAIL_HOST_USER, recipient_list=[srz_data.data['email']])
            return Response({'messages': 'the otpcode successfuly sent to your email', 'status': 'success'}, status=status.HTTP_201_CREATED)

        return Response(srz_data.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegisterConfirm(APIView):
    def post(self, request):
        srz_data = OtpCodeSerializer(data=request.POST)
        print(request.session['user_registration_info'])
        if srz_data.is_valid():
            user_session = request.session['user_registration_info']
            code_instance = OtpCode.objects.get(email=user_session['email']).code

            if int(srz_data.validated_data['code']) == int(code_instance):
                User.objects.create_user(email=user_session['email'], username=user_session['username'],
                                         password=user_session['password'])
                OtpCode.objects.get(email=user_session['email']).delete()
                return Response({'messages': 'user registered successfuly', 'status': 'success'}, status=status.HTTP_201_CREATED)
            return Response({'messages': 'the orp code is wrong', 'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(srz_data.errors, status=status.HTTP_400_BAD_REQUEST)
                


class UserProfile(APIView):
    def get(self, request, user_id=None):
        user = get_object_or_404(User, id=user_id)
        products = Product.objects.filter(user=user)
        srz_user = UserProfileSerializer(instance=user)
        srz_products = ProductSerializer(instance=products, many=True)
        return Response({'data':{'user': srz_user.data, 'products': srz_products.data}, 'status': 'success'}, status=status.HTTP_200_OK)

class UserProfileEdit(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, user_id=None):
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(request, user)
        srz_user = UserProfileEditSerializer(instance=user)
        return Response({'data':{'user': srz_user.data}, 'status': 'success'}, status=status.HTTP_200_OK)



class UserProfileEditConfirm(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def put(self, request, user_id=None):
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(request, user)
        srz_user = UserProfileEditSerializer(instance=user, data=request.data, partial=True)
        if srz_user.is_valid():
            srz_user.save()
            return Response({'data':{'user': srz_user.data}, 'status': 'success'}, status=status.HTTP_200_OK)

        return Response(srz_user.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPanel(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, user_id=None):
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(request, user)
        srz_user = UserProfileSerializer(instance=user)
        products = Product.objects.filter(user=user)
        srz_products = ProductSerializer(instance=products, many=True)
        wallet = get_object_or_404(Wallet, user=user)
        srz_wallet = WalletSerializer(instance=wallet)
        transactions = Transaction.objects.filter(wallet=wallet)
        srz_transaction = TransactionPanelSerializer(instance=transactions, many=True)
        return Response({'data':{'user': srz_user.data, 'products': srz_products.data, 'wallet': srz_wallet.data, 'transactions': srz_transaction.data}, 'status': 'success'}, status=status.HTTP_200_OK)

    
class UserWithdraw(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, user_id=None):
        user = get_object_or_404(User ,id=user_id)
        self.check_object_permissions(request, user)
        wallet = get_object_or_404(Wallet, user=user)
        srz_wallet = WalletSerializer(instance=wallet)
        transactions = Transaction.objects.filter(wallet=wallet)
        srz_transaction = TransactionSerializer(instance=transactions, many=True)
        return Response({'data':{'wallet': srz_wallet.data, 'transactions': srz_transaction.data}, 'status': 'success'}, status=status.HTTP_200_OK)


class UserWithdrawConfirm(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def post(self, request):
        srz_data = TransactionSerializer(data=request.POST)
        if srz_data.is_valid():
            wallet = srz_data.validated_data['wallet']
            user = wallet.user 
            self.check_object_permissions(request, user)
            if wallet.balance >= 500000 and srz_data.validated_data['amount'] >=500000:
                    
                if wallet.balance >= srz_data.validated_data['amount']:
                    srz_data.validated_data['status'] = None
                    srz_data.create(srz_data.validated_data)
                    wallet.balance -= srz_data.validated_data['amount']
                    wallet.save()
                    return Response(srz_data.data, status=status.HTTP_201_CREATED)
                return Response({'message': 'your balance is enough', 'status': 'error'})
            return Response({'message': 'your balance must be more than 500000 toman and withdraw amount too', 'status': 'error'})
        return Response(srz_data.errors, status=status.HTTP_400_BAD_REQUEST)


class UserWithdrawCancel(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def delete(self, request, transaction_id=None):
        transaction = get_object_or_404(Transaction, id=transaction_id)
        wallet = transaction.wallet
        user = wallet.user
        self.check_object_permissions(request, user)
        if transaction.status != True:
            wallet.balance += transaction.amount
            transaction.status = False
            wallet.save()
            transaction.save()
            return Response({'message': 'transaction canceled successfuly', 'status': 'success'}, status=status.HTTP_200_OK)


class UserLogoEdit(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, user_id=None):
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(request, user)
        srz_logo = LogoEditSerializer(instance=user)
        return Response({'data': {'logo': srz_logo.data}, 'status': 'success'}, status=status.HTTP_200_OK)


class UserLogoEditConfirm(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def put(self, request, user_id=None):
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(request, user)
        srz_logo = UserProfileSerializer(instance=user, data=request.data, partial=True)
        if srz_logo.is_valid():
            srz_logo.save()
            return Response({'data':{'logo': srz_logo.data}, 'status': 'success'}, status=status.HTTP_200_OK)

        return Response(srz_logo.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProductAdd(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def post(self, request):
        srz_data = ProductAddSerializer(data=request.POST)
        
        if srz_data.is_valid():
            user = request.user
            self.check_object_permissions(request, user)
            srz_data.validated_data['user'] = request.user
            srz_data.create(srz_data.validated_data)
            return Response(srz_data.data, status=status.HTTP_201_CREATED)
        return Response(srz_data.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProductEdit(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, product_id=None):
        product = get_object_or_404(Product, id=product_id)
        user = product.user
        self.check_object_permissions(request, user)
        srz_data = ProductEditSerializer(instance=product)
        return Response({'data':{'product': srz_data.data}, 'status': 'success'}, status=status.HTTP_200_OK)


class UserProductEditConfirm(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def put(self, request, product_id=None):
        product = get_object_or_404(Product, id=product_id)
        user = product.user
        self.check_object_permissions(request, user)
        srz_data = ProductEditSerializer(instance=product, data=request.data, partial=True)
        if srz_data.is_valid():
            srz_data.save()
            return Response({'data':{'product': srz_data.data}, 'status': 'success'}, status=status.HTTP_200_OK)

        return Response(srz_data.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProductDelete(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def delete(self, request, product_id=None):
        product = get_object_or_404(Product, id=product_id)
        user = product.user
        self.check_object_permissions(request, user)
        product.delete()
        return Response({'message': 'product deleted successfuly', 'status': 'success'}, status=status.HTTP_200_OK)    
