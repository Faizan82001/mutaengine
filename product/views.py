import logging
from product.models import Product
from product.serializers import ProductSerializer
from mutaengine.base_view import BaseAPIView
from mutaengine.utils import custom_response
from rest_framework import status, generics, exceptions
from rest_framework.permissions import IsAuthenticated


logger = logging.getLogger(__name__)


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
            logger.error(f"{request.user.username} tried to create a product. Data:{request.data}")
            raise exceptions.PermissionDenied
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"{request.user.username} added new product.\nDetails: {serializer.data}")
            return custom_response(
                message="Product added successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        logger.error(f"{request.user.username} failed to add new Product.\nError:{serializer.errors}")
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
            logger.error(f"{request.user.username} tried to update a product.\nData:{request.data}")
            raise exceptions.PermissionDenied
        product_id = kwargs.get('id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            logger.info(f"{request.user.username} tried to update non existing product with id: {product_id}")
            return custom_response(
                message="Product not found",
                data={},
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"{request.user.username} successfully updated a product with id({product.id}).\nData:{serializer.data}")
            return custom_response(
                message="Product updated successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        logger.error(f"{request.user.username} failed to update product with id({product.id}).\nError:{serializer.errors}")
        return custom_response(
            message="Validation Error",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def delete_product(self, request, *args, **kwargs):
        product_id = kwargs.get('id')
        if not request.user.is_superuser:
            logger.error(f"{request.user.username} tried to delete a product with id({product_id})")
            raise exceptions.PermissionDenied
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            logger.info(f"{request.user.username} tried to delete non existing product with id: {product_id}")
            return custom_response(
                message="Product not found",
                data={},
                status_code=status.HTTP_404_NOT_FOUND
            )
        product.delete()
        logger.info(f"{request.user.username} successfully deleted a product with id({product.id})")
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
