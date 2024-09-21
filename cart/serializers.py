from rest_framework import serializers
from cart.models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    total_price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_title', 'product_price', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_cart_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_cart_price']

    def get_total_cart_price(self, obj):
        return sum([item.total_price for item in obj.items.all()])
