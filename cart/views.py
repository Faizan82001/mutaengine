from rest_framework import status, exceptions
from .models import Cart, CartItem
from product.models import Product
from .serializers import CartSerializer, CartItemSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from mutaengine.base_view import BaseAPIView
from mutaengine.utils import custom_response


class CartView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def get_cart(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return custom_response(
            message="Cart retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def add_to_cart(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity') or 1

        if not product_id:
            return custom_response(
                message="Product ID is required",
                data={},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        product = Product.objects.filter(id=product_id).first()
        if not product:
            raise exceptions.NotFound
        
        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity = cart_item.quantity + int(quantity)
        cart_item.save()

        return custom_response(
            message="Product added to cart",
            data=CartItemSerializer(cart_item).data,
            status_code=status.HTTP_200_OK
        )

    def remove_from_cart(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        if not product_id:
            return custom_response(
                message="Product ID is required",
                data={},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            raise exceptions.NotFound
        
        cart_item = CartItem.objects.filter(cart=cart, product__id=product_id).first()
        if not cart_item:
            return custom_response(
                message="Product not in cart",
                data={},
                status_code=status.HTTP_404_NOT_FOUND
            )

        if not quantity or cart_item.quantity < quantity:
            cart_item.delete()
        else:
            cart_item.quantity -= quantity
            cart_item.save()

        return custom_response(
            message="Product removed from cart",
            data={},
            status_code=status.HTTP_204_NO_CONTENT
        )

    def get(self, request, *args, **kwargs):
        return self.handle_request(request, self.get_cart, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.handle_request(request, self.add_to_cart, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.handle_request(request, self.remove_from_cart, *args, **kwargs)
