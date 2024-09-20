from product.models import Product
from product.serializers import ProductSerializer
from rest_framework import status, generics, exceptions
from rest_framework.permissions import IsAuthenticated
from mutaengine.base_view import BaseAPIView
from mutaengine.utils import custom_response

class ProductListCreateView(BaseAPIView, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def list_products(self, request, *args, **kwargs):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return custom_response(
            message="Products fetched successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    def create_product(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise exceptions.PermissionDenied
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return custom_response(
                message="Product added successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return custom_response(
            message="Validation Error",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def get(self, request, *args, **kwargs):
        return self.handle_request(request, self.list_products, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.handle_request(request, self.create_product, *args, **kwargs)


class ProductRetrieveUpdateDeleteView(BaseAPIView, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_product(self, request, *args, **kwargs):
        product_id = kwargs.get('id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return custom_response(
                message="Product not found",
                data={},
                status_code=status.HTTP_404_NOT_FOUND
            )
        serializer = ProductSerializer(product)
        return custom_response(
            message="Product fetched successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    def update_product(self, request, *args, **kwargs):
        product_id = kwargs.get('id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return custom_response(
                message="Product not found",
                data={},
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return custom_response(
                message="Product updated successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        return custom_response(
            message="Validation Error",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def delete_product(self, request, *args, **kwargs):
        product_id = kwargs.get('id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return custom_response(
                message="Product not found",
                data={},
                status_code=status.HTTP_404_NOT_FOUND
            )
        product.delete()
        return custom_response(
            message="Product deleted successfully",
            data={},
            status_code=status.HTTP_204_NO_CONTENT
        )
    
    def get(self, request, *args, **kwargs):
        return self.handle_request(request, self.get_product, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        return self.handle_request(request, self.update_product, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        return self.handle_request(request, self.update_product, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self.handle_request(request, self.delete_product, *args, **kwargs)

# class GetAllItemsView(BaseAPIView):
#     permission_classes = [IsAuthenticated,]
#     def get_all_items(self, request, *args, **kwargs):
#         try:
#             response = requests.get('https://fakestoreapi.com/products')
#             response.raise_for_status()
#             products = response.json()
#             return custom_response(
#                 message="Products fetched successfully",
#                 data=products,
#                 status_code=status.HTTP_200_OK
#             )
#         except requests.exceptions.RequestException as e:
#             raise Exception(f"Failed to fetch products: {str(e)}")

#     def get(self, request, *args, **kwargs):
#         return self.handle_request(request, self.get_all_items)

# class RetrieveUpdateDestroyItemView(BaseAPIView, generics.RetrieveUpdateDestroyAPIView):
#     permission_classes = [IsAuthenticated,]
    
#     def get_item(self, request, *args, **kwargs):
#         response = requests.get(f"https://fakestoreapi.com/products/{kwargs.get('item_id')}")
#         response.raise_for_status()
#         item = response.json()
#         return custom_response(data=item, message="Item retrieved successfully.", status_code=status.HTTP_200_OK)
        
#     def update_item(self, request, *args, **kwargs):
#         response = requests.put(f"https://fakestoreapi.com/products/{kwargs.get('item_id')}", json=request.data)
#         response.raise_for_status()
#         updated_item = response.json()
#         return custom_response(data=updated_item, message="Item updated successfully.", status_code=status.HTTP_200_OK)
    
#     def delete_item(self, request, *args, **kwargs):
#         response = requests.delete(f"https://fakestoreapi.com/products/{kwargs.get('item_id')}", json=request.data)
#         response.raise_for_status()
#         updated_item = response.json()
#         return custom_response(data=updated_item, message="Item updated successfully.", status_code=status.HTTP_200_OK)
    
#     def get(self, request, *args, **kwargs):
#         return self.handle_request(request, self.get_item, *args, **kwargs)
    
#     def put(self, request, *args, **kwargs):
#         return self.handle_request(request, self.update_item, *args, **kwargs)

#     def patch(self, request, *args, **kwargs):
#         return self.handle_request(request, self.update_item, *args, **kwargs)
    
#     def delete(self, request, *args, **kwargs):
#         return self.handle_request(request, self.delete_item, *args, **kwargs)