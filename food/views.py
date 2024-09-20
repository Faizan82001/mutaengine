
import paypalrestsdk
import requests
import random
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ExternalMealListView(APIView):
    def get(self, request):
        api_url = "https://www.themealdb.com/api/json/v1/1/search.php?s="
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            meals = data.get('meals', [])

            # Format the data
            formatted_meals = [
                {
                    "id": meal['idMeal'],
                    "name": meal['strMeal'],
                    "description": meal['strInstructions'],
                    "price": random.randint(10,20),
                    "image_url": meal['strMealThumb']
                }
                for meal in meals
            ]
            return Response(formatted_meals, status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

class CreatePaymentView(APIView):
    def post(self, request):
        try:
            amount = request.data.get('amount', '10.00')
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": "http://localhost:8000/paypal-return/",
                    "cancel_url": "http://localhost:8000/paypal-cancel/"
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": "Item",
                            "sku": "item",
                            "price": amount,
                            "currency": "USD",
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": amount,
                        "currency": "USD"
                    },
                    "description": "This is the payment transaction description."
                }]
            })

            if payment.create():
                return Response({'approval_url': payment['links'][1]['href']}, status=status.HTTP_200_OK)
            else:
                return Response({'error': payment.error}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
