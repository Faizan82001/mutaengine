from django.urls import path
from .views import OrderView, StripeWebhookView

app_name = 'order'

urlpatterns = [
    path('order/', OrderView.as_view(), name='place_order'),  # Place an order and initiate payment
    # path('order/<int:order_id>/capture/', OrderView.as_view(), name='paypal_capture'),  # Capture PayPal payment
    # path('orders/', OrderView.as_view(), name='get_orders'),  # Get all user orders
    path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
]
