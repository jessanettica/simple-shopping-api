"""ecommercesite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
"""
from django.contrib import admin
from django.conf.urls import url, include
from rest_framework import routers
from shop import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'carts', views.CartViewSet)
router.register(r'cart_items', views.CartItemViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'order_items', views.OrderItemViewSet)

# Wire up the API using automatic URL routing
# Also include login URLs for the browsable API
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
