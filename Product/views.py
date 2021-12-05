from django.shortcuts import render

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.request import Request
from Product.models import Product
from Product.serializers import ProductSerializer
from rest_framework.decorators import api_view
from ResponseUtil import Response
import Product.dynamo.dynamodb as db
import json
from ConstantUtil import Constant
from django.core.paginator import Paginator
# Create your views here.

@api_view(['GET', 'POST'])
def product_list(request):
    params = request.query_params
    if request.method == 'GET':
        fields = []
        count = 10
        page_no = 0
        try:
            str = params.get('fields', '')
            if str != '':
                fields = str.split(',')
            limit = int(params.get('limit', '10'))
            offset = int(params.get('offset', '0'))
            count = limit
            page_no = offset/limit
        except ValueError:
            print("use default config")

        products = Product.objects.all()
        page = Paginator(products, count)
        products = page.get_page(page_no+1)
        product_serializer = ProductSerializer(products, many=True)
        records = product_serializer.data
        if len(fields) > 0:
            records = []
            for row in product_serializer.data:
                new_row = {}
                for field in fields:
                    if field in ProductSerializer.Meta.fields:
                        new_row[field] = row.get(field)
                records.append(new_row)
        #Get 200
        return JsonResponse(Response().success(records), safe=False, status=status.HTTP_200_OK)
            # 'safe=False' for objects serialization

    elif request.method == 'POST':
        product_data = JSONParser().parse(request)
        print(product_data)
        product_serializer = ProductSerializer(data=product_data)
        if product_serializer.is_valid():
            product_serializer.save()
            # Create 201
            return JsonResponse(Response().success(product_serializer.data), status=status.HTTP_201_CREATED)
        #Invalid Data 400
        return JsonResponse(Response().resp({}, Constant().BAD_DATA), status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        # 404 not found
        return JsonResponse({'message': 'The product does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        product_serializer = ProductSerializer(product)
        return JsonResponse(Response().success(product_serializer.data), status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        product_data = JSONParser().parse(request)
        product_serializer = ProductSerializer(product, data=product_data)
        if product_serializer.is_valid():
            product_serializer.save()
            return JsonResponse(Response().resp(Constant().POST,product_serializer.data), status=status.HTTP_201_CREATED)
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
            if db.get_item("comments", filter) != None:
                return JsonResponse({'message': 'You can only add one comment for one product!'}, status=status.HTTP_404_NOT_FOUND)
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