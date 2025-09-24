from decimal import Decimal, ROUND_HALF_UP
from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product
from products.serializers import ProductSerializer
from notifications.utils import NotificationService


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Order items 
    """
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'unit_price', 'total_price']
        read_only_fields = ['id', 'unit_price', 'total_price']

    def create(self, validated_data):
        product_id = validated_data.pop("product_id")
        product = Product.objects.get(id=product_id)

        unit_price = product.price
        quantity = validated_data.get("quantity", 1)
        total_price = unit_price * quantity

        return OrderItem.objects.create(
            product=product,
            unit_price=unit_price,
            total_price=total_price,
            **validated_data
        )


class OrderSerializer(serializers.ModelSerializer):
    """
    Orders
    """
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
        read_only_fields = [
            'id', 'order_number', 'customer', 'subtotal', 
            'tax_amount', 'total_amount', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)

        subtotal = Decimal('0.00')
        for item_data in items_data:
            serializer = OrderItemSerializer(data=item_data)
            serializer.is_valid(raise_exception=True)
            item = serializer.save(order=order)
            subtotal += item.total_price

        # Round subtotal and calculate tax
        order.subtotal = subtotal.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        order.tax_amount = (order.subtotal * Decimal('0.16')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        order.total_amount = (order.subtotal + order.tax_amount + order.shipping_cost).quantize(
            Decimal('1'), rounding=ROUND_HALF_UP
        )

        order.save()

        # Send notifications
        NotificationService.send_order_sms(order)
        NotificationService.send_order_email_to_admin(order)

        return order
