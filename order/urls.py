from order.views import OrderView, StripeWebhookView
from django.urls import path

app_name = 'order'

urlpatterns = [
    path('order/', OrderView.as_view(), name='place_order'),
    path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
]
