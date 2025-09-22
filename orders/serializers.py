from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'unit_price', 'total_price']
        read_only_fields = ['id', 'total_price']

    def create(self, validated_data):
        validated_data['total_price'] = validated_data['unit_price'] * validated_data['quantity']
        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'customer',
            'status',
            'subtotal',
            'tax_amount',
            'shipping_cost',
            'total_amount',
            'shipping_address',
            'billing_address',
            'items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at', 'total_amount']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)

        subtotal = 0
        for item_data in items_data:
            order_item = OrderItem.objects.create(order=order, **item_data)
            subtotal += order_item.total_price

        order.subtotal = subtotal
        order.total_amount = subtotal + order.tax_amount + order.shipping_cost
        order.save()
        return order
