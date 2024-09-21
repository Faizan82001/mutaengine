from product.models import Product
from product.serializers import ProductSerializer
from mutaengine.base_view import BaseAPIView
from mutaengine.utils import custom_response
from rest_framework import status, generics, exceptions
from rest_framework.permissions import IsAuthenticated

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
        if not request.user.is_superuser:
            raise exceptions.PermissionDenied
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
        if not request.user.is_superuser:
            raise exceptions.PermissionDenied
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
