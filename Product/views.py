from django.shortcuts import render

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status

from Product.models import Product
from Product.serializers import ProductSerializer
from rest_framework.decorators import api_view
from ResponseUtil import Response

import Product.dynamo.dynamodb as db
import json
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

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def product_comments(request, pk):
    filter = {"comment_id": pk}
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return JsonResponse({'message': 'The product does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if db.get_item("comments", filter) == None:
            return JsonResponse({'message': 'The comment does not exist'}, status=status.HTTP_404_NOT_FOUND)
        res = db.find_by_template("comments", filter)
        print("test_filter: result = \n", json.dumps(res, indent=3))
        return JsonResponse(Response().success(res), status=status.HTTP_200_OK)

    elif request.method == 'POST':
        if request.POST.get("response") != None:
            if db.get_item("comments", filter) == None:
                return JsonResponse({'message': 'The comment does not exist'}, status=status.HTTP_404_NOT_FOUND)
            params = {}
            for key, value in request.POST.items():
                print(f'Key: {key}')
                print(f'Value: {value}')
                params[key] = value
            params["comment_id"] = pk

            if db.is_valid_response(params):
                res = db.add_response("comments", params["comment_id"], params["commenter_email"], params["response"])
                return JsonResponse(Response().success(res), status=status.HTTP_200_OK)
            return JsonResponse(Response().failed(), status=status.HTTP_404_NOT_FOUND)
        else:
            if request.POST.get("comment") != None:
                params = {}
                for key, value in request.POST.items():
                    print(f'Key: {key}')
                    print(f'Value: {value}')
                    params[key] = value
                params["comment_id"] = pk
            else:
                return JsonResponse({'message': 'Nothing post!'}, status=status.HTTP_404_NOT_FOUND)

            if db.is_valid_comment(params):
                res = db.add_comment(params["comment_id"], params["email"], params["comment"], params["tags"])
                return JsonResponse(Response().success(res), status=status.HTTP_200_OK)
            return JsonResponse(Response().failed(), status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'PUT':
        if db.get_item("comments", filter) == None:
            return JsonResponse({'message': 'The comment does not exist'}, status=status.HTTP_404_NOT_FOUND)
        if request.POST.get("comment") != None:
            params = {}
            for key, value in request.POST.items():
                print(f'Key: {key}')
                print(f'Value: {value}')
                params[key] = value
            params["comment_id"] = pk
        else:
            return JsonResponse({'message': 'Nothing update!'}, status=status.HTTP_404_NOT_FOUND)

        if db.is_valid_new_comment(params):
            res = db.update_comment(params["comment_id"], params["comment"])
            return JsonResponse(Response().success(res), status=status.HTTP_200_OK)
        return JsonResponse(Response().failed(), status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'DELETE':
        if db.delete_item("comments", filter):
            return JsonResponse(Response().success({}), status=status.HTTP_200_OK)
        else:
            return JsonResponse(Response().failed(), status=status.HTTP_404_NOT_FOUND)