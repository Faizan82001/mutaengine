import logging
from cart.models import Cart, CartItem
from cart.serializers import CartSerializer, CartItemSerializer
from product.models import Product
from mutaengine.base_view import BaseAPIView
from mutaengine.utils import custom_response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, exceptions


logger = logging.getLogger(__name__)


class CartView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def get_cart(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        logger.info(f"User {request.user.username} retrieved cart successfully")
        return custom_response(
            message="Cart retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def add_to_cart(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity') or 1

        if not product_id:
            logger.exception(f"{request.user.username}'s request is missing product_id")
            return custom_response(
                message="Product ID is required",
                data={},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        product = Product.objects.filter(id=product_id).first()
        if not product:
            logger.exception(f"{request.user.username} tried to add product with id {product_id}")
            raise exceptions.NotFound
        
        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity = cart_item.quantity + int(quantity)
        cart_item.save()
        cart_item_data = CartItemSerializer(cart_item).data
        
        logger.info(f"Cart updated by user: {request.user.username}\nAdded Cart Item: {cart_item_data}")
        return custom_response(
            message="Product added to cart",
            data=cart_item_data,
            status_code=status.HTTP_200_OK
        )

    def remove_from_cart(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        if not product_id:
            logger.exception(f"{request.user.username}'s request is missing product_id")
            return custom_response(
                message="Product ID is required",
                data={},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            logger.info(f"{request.user.username} has no cart")
            raise exceptions.NotFound
        
        cart_item = CartItem.objects.filter(cart=cart, product__id=product_id).first()
        if not cart_item:
            logger.info(f"{request.user.username} tried to remove invalid cart item: {product_id}")
            return custom_response(
                message="Product not in cart",
                data={},
                status_code=status.HTTP_404_NOT_FOUND
            )

        if not quantity or cart_item.quantity < quantity:
            logger.info(f"{request.user.username} removed product with id({cart_item.product.id}) from the cart")
            cart_item.delete()
        else:
            cart_item.quantity -= quantity
            cart_item.save()
            logger.info(f"{request.user.username} decreased product with id({cart_item.product.id})'s quantity by {quantity}")

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
