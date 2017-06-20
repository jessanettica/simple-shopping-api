from shop.models import *
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'instagram_handle')

class ProductSerializer(serializers.ModelSerializer):

    """Serializer for the Product model."""

    class Meta:
        model = Product
        fields = (
            'id', 'price', 'title', 'available_inventory'
        )

class CartSerializer(serializers.ModelSerializer):

    """Serializer for the Cart model."""

    customer = UserSerializer(read_only=True)
    # used to represent the target of the relationship using its __unicode__ method
    items = serializers.StringRelatedField(many=True)

    class Meta:
        model = Cart
        fields = (
            'id', 'customer', 'created_at', 'updated_at', 'items'
        )

class CartItemSerializer(serializers.ModelSerializer):

    """Serializer for the CartItem model."""

    cart = CartSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = (
            'id', 'cart', 'product', 'quantity'
        )


class OrderSerializer(serializers.ModelSerializer):

    """Serializer for the Order model."""

    customer = UserSerializer(read_only=True)
    # used to represent the target of the relationship using its __unicode__ method
    order_items = serializers.StringRelatedField(many=True, required=False)

    class Meta:
        model = Order
        fields = (
            'id', 'customer', 'total', 'created_at', 'updated_at', 'order_items'
        )

    def create(self, validated_data):
        """Override the creation of Order objects

        Parameters
        ----------
        validated_data: dict

        """
        order = Order.objects.create(**validated_data)
        return order

class OrderItemSerializer(serializers.ModelSerializer):

    """Serializer for the OrderItem model."""

    order = OrderSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            'id', 'order', 'product', 'quantity'
        )
