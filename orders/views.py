from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from permissions import IsOwnerOrReadOnly
from accounts.models import Product
from accounts.serializers import ProductSerializer
from .serializers import CartItemAddSerializer, CouponSerializer, OrderDetailSerializer, OrderItemSerializer
from .models import Coupon, Order, OrderItem
from .cart import Cart
import json
import requests
import datetime


class CartVieww(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = Cart(request)
        cart_items = [cartitem for cartitem in cart]
        product_ids = [cart_item['product'].id for cart_item in cart_items]
        products = Product.objects.filter(id__in=product_ids)
        srz_data = ProductSerializer(instance=products, many=True)
        return Response({'data': srz_data.data, 'status': 'success'}, status=status.HTTP_200_OK)

class CartAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        cart = Cart(request)
        srz_data = CartItemAddSerializer(data=request.data)
        if srz_data.is_valid():
            product = get_object_or_404(Product, id=product_id)
            cart.add(product, quantity=int(srz_data.data['quantity']))
            return Response(data=srz_data.data, status=status.HTTP_201_CREATED)


class CartRemoveView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        return Response({'message': 'cart item removed from cart'}, status=status.HTTP_200_OK)


class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = Cart(request)
        order = Order.objects.create(user=request.user)
        for item in cart:
            OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])

        cart.clear()
        return Response({'message': 'Order created successfuly', 'status': 'success'}, status=status.HTTP_201_CREATED)

class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        user = order.user
        self.check_object_permissions(request, user)
        srz_data = OrderDetailSerializer(instance=order)
        srz_items = OrderItemSerializer(instance=order.items, many=True)
        return Response({'data':{'order': srz_data.data, 'items': srz_items.data}, 'status': 'success'}, status=status.HTTP_200_OK)


MERCHANT = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"
CallbackURL = 'http://127.0.0.1:8000/orders/verify/'


class OrderPayView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        request.session['order_pay'] = {
			'order_id': order.id,
		}
        req_data = {
			"merchant_id": MERCHANT,
			"amount": order.get_total_price(),
			"callback_url": CallbackURL,
			"description": description,
			"metadata": {"mobile": request.user.phone_number, "email": request.user.email}
		}
        req_header = {"accept": "application/json",
					  "content-type": "application/json'"
                      }
        req = requests.post(url=ZP_API_REQUEST, data=json.dumps(
			req_data), headers=req_header)
        authority = req.json()['data']['authority']

        if len(req.json()['errors']) == 0:
            return Response({'status': 'success', 'data': {'url': ZP_API_STARTPAY.format(authority=authority)}}, status=status.HTTP_202_ACCEPTED)
        else:
            error_code = req.json()['errors']['code']
            error_message = req.json()['errors']['message']
            return Response({'message': f"Error code: {error_code}, Error Message: {error_message}"}, status=status.HTTP_406_NOT_ACCEPTABLE)



class OrderVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        order_id = request.session['order_pay']['order_id']
        order = Order.objects.get(id=int(order_id))
        t_status = request.GET.get('Status')
        t_authority = request.GET['Authority']

        if request.GET.get('Status') == 'OK':
            req_header = {"accept": "application/json",
                        "content-type": "application/json'"}
            req_data = {
                "merchant_id": MERCHANT,
                "amount": order.get_total_price(),
                "authority": t_authority
            }

            req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
            if len(req.json()['errors']) == 0:
                t_status = req.json()['data']['code']
                if t_status == 100:
                    order.paid = True
                    order.save()
                    return Response({'message': 'Transaction success.\nRefID: ' + str(
                        req.json()['data']['ref_id'])}
                    )
                elif t_status == 101:
                    return Response({'message': 'Transaction submitted.\nStatus: ' + str(
                        req.json()['data']['message'])}
                    )
                else:
                    return Response({'message': 'Transaction failed.\nStatus: ' + str(
                        req.json()['data']['message'])}
                    )
            else:
                e_code = req.json()['errors']['code']
                e_message = req.json()['errors']['message']
                return Response({'message': f"Error code: {e_code}, Error Message: {e_message}", 'status': 'error'})
        else:
            return Response({'message': 'Transaction failed or canceled by user', 'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


class CouponApplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        now = datetime.datetime.now()
        srz_coupon = CouponSerializer(data=request.POST)

        if srz_coupon.is_valid():
            code = srz_coupon.validated_data['code']
            try:
                coupon = Coupon.objects.get(code__exact=code, valid_from__lte=now, valid_to__gte=now, active=True)

            except Coupon.DoesNotExist:
                return Response({'message': 'this coupon does not exists', 'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)

            order = get_object_or_404(Order, id=order_id)
            order.discount = coupon.discount
            order.save()
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        return Response(data=srz_coupon.errors, status=status.HTTP_400_BAD_REQUEST)