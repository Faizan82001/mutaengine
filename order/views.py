import stripe
import logging
from cart.models import Cart
from order.models import Order, OrderItem
from order.serializers import OrderSerializer
from mutaengine.base_view import BaseAPIView
from mutaengine.utils import custom_response, send_invoice_email
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import exceptions, permissions, status


stripe.api_key = settings.STRIPE_SECRET_KEY


class OrderView(BaseAPIView):
    logger = logging.getLogger(__name__)
    permission_classes = [permissions.IsAuthenticated]

    def create_order(self, request, *args, **kwargs):
        self.logger.info(f"{request.user.username} is attempting to create an order.")

        # Get cart items for the user
        cart = Cart.objects.filter(user=request.user).first()
        
        if not cart:
            self.logger.info(f"{request.user.username} tried to order with unknown cart")
            raise exceptions.NotFound("Cart Not Found")
        
        cart_items = cart.items.all()
        
        if not cart_items.exists():
            self.logger.info(f"{request.user.username} tried to order with empty cart")
            return custom_response(
                message="Your cart is empty.",
                data={},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate total amount from cart
        total_amount = sum(item.total_price for item in cart_items)
        self.logger.info(f"Total amount calculated for {request.user.username}'s order: ${total_amount:.2f}")

        try:
            # Create a Stripe PaymentIntent
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': 'Total Cart Purchase',
                            },
                            'unit_amount': int(total_amount * 100),  # Convert to cents
                        },
                        'quantity': 1
                    },
                ],
                mode='payment',
                success_url=settings.AFTER_PAYMENT_REDIRECT_URL,
                cancel_url=settings.AFTER_PAYMENT_REDIRECT_URL,
            )
            self.logger.info(f"Stripe PaymentIntent created successfully")

            # Create the Order in your database
            order = Order.objects.create(
                user=request.user,
                external_order_id=session['id'],
                total_amount=total_amount,
                payment_url=session['url'],
                status="PENDING"
            )
            self.logger.info(f"Order created successfully with ID: {order.id}")
            
            for item in cart_items:
                OrderItem.objects.create(
                   order=order,
                   product=item.product,
                   quantity=item.quantity,
                   price=item.total_price,
                )
                self.logger.debug(f"Added item to order: {item.product.title}, Quantity: {item.quantity}")

            # cart_items.delete()

            return custom_response(
                message="Order created successfully.",
                data={
                    "checkout_url": session['url'],
                    "order_id": order.id
                },
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            self.logger.error(f"500 Error: {str(e)}")
            return custom_response(
                message="Failed to create Stripe payment intent.",
                data={"error": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Get all user orders
    def get_user_orders(self, request):
        self.logger.info(f"{request.user.username} is fetching their orders.")
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return custom_response(
            message="Orders fetched successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    # Handle different HTTP methods
    def get(self, request, *args, **kwargs):
        return self.handle_request(request, self.get_user_orders)

    def post(self, request, *args, **kwargs):
        return self.handle_request(request, self.create_order)


class StripeWebhookView(BaseAPIView):
    logger = logging.getLogger('stripe_webhook')
    permission_classes = []

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
            self.logger.info('Webhook received: %s', event)
        except ValueError as e:
            # Invalid payload
            self.logger.error('Invalid payload: %s', str(e))
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            self.logger.error('Invalid signature: %s', str(e))  # Log error for invalid signature
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle the event
        session = event['data']['object']
        order = Order.objects.filter(external_order_id=session['id']).first()

        if event['type'] == 'checkout.session.completed':
            # Find the order based on the Stripe Checkout Session ID
            cart = Cart.objects.filter(user=order.user).first()

            if order:
                # Mark the order as completed
                order.status = 'COMPLETED'

                cart.items.all().delete()     # Clear Cart
                self.logger.info(f"Cart for user({order.user.username}) has been cleared")
                
                # Send Invoice Email
                send_invoice_email(order.user, order)
                order.save()
                self.logger.info(f"Order status for Order#{order.id} has been changed to Completed.")
        
        elif event['type'] == 'payment_intent.payment_failed':
            # Find the order based on the Stripe Checkout Session ID
            if order:
                # Mark the order as completed
                order.status = 'FAILED'
                order.save()
                self.logger.info(f"Order status for Order#{order.id} has been changed to Failed.")
                self.logger.info('Order marked as failed: %s', order.id)

        return JsonResponse({'status': 'success'}, status=status.HTTP_200_OK)
