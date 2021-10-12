from django.shortcuts import render

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status

from Product.models import Product
from Product.serializers import ProductSerializer
from rest_framework.decorators import api_view
from ResponseUtil import Response
# Create your views here.

@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        products = Product.objects.all()
        product_serializer = ProductSerializer(products, many=True)
        return JsonResponse(Response().success(product_serializer.data), safe=False, status=status.HTTP_200_OK)
        # 'safe=False' for objects serialization

    elif request.method == 'POST':
        print(request)
        product_data = JSONParser().parse(request)
        product_serializer = ProductSerializer(data=product_data)
        if product_serializer.is_valid():
            product_serializer.save()
            return JsonResponse(Response().success(product_serializer.data), status=status.HTTP_200_OK)
        return JsonResponse(Response().failed(), status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return JsonResponse({'message': 'The product does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        product_serializer = ProductSerializer(product)
        return JsonResponse(Response().success(product_serializer.data), status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        product_data = JSONParser().parse(request)
        product_serializer = ProductSerializer(product, data=product_data)
        if product_serializer.is_valid():
            product_serializer.save()
            return JsonResponse(Response().success(product_serializer.data), status=status.HTTP_200_OK)
        return JsonResponse(Response().failed(), status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'DELETE':
        product.delete()
        return JsonResponse(Response().success({}), status=status.HTTP_200_OK)