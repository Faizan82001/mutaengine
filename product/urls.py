from django.urls import path
from .views import ProductListCreateView, ProductRetrieveUpdateDeleteView

app_name = 'products'

urlpatterns = [
    path('', ProductListCreateView.as_view(), name='product_list_create'),  # List and create products
    path('<int:id>/', ProductRetrieveUpdateDeleteView.as_view(), name='product_retrieve_update_delete'),  # Retrieve, update, and delete products
]
