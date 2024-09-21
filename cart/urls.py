from cart.views import CartView
from django.urls import path

app_name = 'cart'

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
]
