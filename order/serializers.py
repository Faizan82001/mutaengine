from order.models import Order, OrderItem
from rest_framework import serializers


class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    total_price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_title', 'product_price', 'quantity', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total_amount', 'external_order_id', 'payment_url', 'status', 'created_at']
