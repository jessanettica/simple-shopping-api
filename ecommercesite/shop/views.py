# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.db.models import FloatField
from django.db.models import F
from django.db.models import Sum

from rest_framework import viewsets
from rest_framework import serializers
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.decorators import list_route
from rest_framework.response import Response

from shop.models import *
from shop.serializers import *



class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed or edited.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CartViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows carts to be viewed or edited.
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    @detail_route(methods=['post', 'put'])
    def add_to_cart(self, request, pk=None):
        """Add an item to a user's cart.

        Adding to cart is disallowed if there is not enough inventory for the
        product available. If there is, the quantity is increased on an existing
        cart item or a new cart item is created with that quantity and added
        to the cart.

        Parameters
        ----------
        request: request

        Return the updated cart.

        """
        cart = self.get_object()
        try:
            product = Product.objects.get(
                pk=request.data['product_id']
            )
            quantity = int(request.data['quantity'])
        except Exception as e:
            print e
            return Response({'status': 'fail'})

        # Disallow adding to cart if available inventory is not enough
        if product.available_inventory <= 0 or product.available_inventory - quantity <= 0:
            print "There is no more product available"
            return Response({'status': 'fail'})

        existing_cart_item = CartItem.objects.filter(cart=cart,product=product).first()
        # before creating a new cart item check if it is in the cart already
        # and if yes increase the quantity of that item
        if existing_cart_item:
            existing_cart_item.quantity += quantity
            existing_cart_item.save()
        else:
            new_cart_item = CartItem(cart=cart, product=product, quantity=quantity)
            new_cart_item.save()

        # return the updated cart to indicate success
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @detail_route(methods=['post', 'put'])
    def remove_from_cart(self, request, pk=None):
        """Remove an item from a user's cart.

        Like on the Everlane website, customers can only remove items from the
        cart 1 at a time, so the quantity of the product to remove from the cart
        will always be 1. If the quantity of the product to remove from the cart
        is 1, delete the cart item. If the quantity is more than 1, decrease
        the quantity of the cart item, but leave it in the cart.

        Parameters
        ----------
        request: request

        Return the updated cart.

        """
        cart = self.get_object()
        try:
            product = Product.objects.get(
                pk=request.data['product_id']
            )
        except Exception as e:
            print e
            return Response({'status': 'fail'})

        try:
            cart_item = CartItem.objects.get(cart=cart,product=product)
        except Exception as e:
            print e
            return Response({'status': 'fail'})

        # if removing an item where the quantity is 1, remove the cart item
        # completely otherwise decrease the quantity of the cart item
        if cart_item.quantity == 1:
            cart_item.delete()
        else:
            cart_item.quantity -= 1
            cart_item.save()

        # return the updated cart to indicate success
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class CartItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows cart items to be viewed or edited.
    """
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows orders to be viewed or created.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


    def perform_create(self, serializer):
        """Add info and perform checks before saving an Order.

        Before creating an Order, there is a check on the customer's cart items.
        If the cart item quantity causes the product's available inventory to
        dip below zero, a validation error is raised.If there is enough inventory to support the order, an Order is created
        and cart items are used to make order items. After that the cart is
        cleared.

        NOTE: Cart items are not deleted. When the cart is cleared the cart items
        still exist but are disassociated from the cart. The cart is empty so
        that the user can add new things to it, but cart items are preserved as
        they could be helpful in drawing insights from customer behavior or making
        suggestions. For example, what they have put in their cart previously,
        what other similar products might she/he like, etc.

        Parameters
        ----------
        serializer: OrderSerialiazer
            Serialized representation of Order we are creating.

        """

        try:
            purchaser_id = self.request.data['purchaser']
            user = User.objects.get(pk=purchaser_id)
        except:
            raise serializers.ValidationError(
                'User was not found'
            )

        cart = user.cart

        for cart_item in cart.items.all():
            if cart_item.product.available_inventory - cart_item.quantity < 0:
                raise serializers.ValidationError(
                    'We do not have enough inventory of ' + str(cart_item.product.title) + \
                    'to complete your purchase. Sorry, we will restock soon'
                )

        # find the order total using the quantity of each cart item and the product's price
        total_aggregated_dict = cart.items.aggregate(total=Sum(F('quantity')*F('product__price'),output_field=FloatField()))
        order_total = round(total_aggregated_dict['total'], 2)

        order = serializer.save(customer=user, total=order_total)

        order_items = []
        for cart_item in cart.items.all():
            order_items.append(OrderItem(order=order, product=cart_item.product, quantity=cart_item.quantity))
            # available_inventory should decrement by the appropriate amount
            cart_item.product.available_inventory -= cart_item.quantity
            cart_item.product.save()


        OrderItem.objects.bulk_create(order_items)
        # use clear instead of delete since it removes all objects from the
        # related object set. It doesnot delete the related objects it just
        # disassociates them, which is what we want in order to empty the cart
        # but keep cart items in the db for customer data analysis
        cart.items.clear()

    def create(self, request, *args, **kwargs):
        """Override the creation of Order objects.

        Parameters
        ----------
        request: dict
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @list_route()
    def order_history(self, request):
        """Return a list of a user's orders.

        Parameters
        ----------
        request: request

        """
        user_id = request.GET.get('user_id', 0)

        try:
            user = User.objects.get(id=user_id)

        except:
            # no user was found, so order history cannot be retrieved.
            return Response({'status': 'fail'})

        orders = Order.objects.filter(customer=user)
        serializer = OrderSerializer(orders, many=True)

        return Response(serializer.data)



class OrderItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows order items to be viewed or edited.
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
