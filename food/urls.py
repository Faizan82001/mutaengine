# urls.py

from django.urls import path
from .views import ExternalMealListView, CreatePaymentView

urlpatterns = [
    path('external-meals/', ExternalMealListView.as_view(), name='external_meal_list'),
    path('create-payment/', CreatePaymentView.as_view(), name='create_payment'),
]
