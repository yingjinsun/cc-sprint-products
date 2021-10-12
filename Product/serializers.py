from rest_framework import serializers
from Product.models import Product


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('product_id',
                  'product_name',
                  'category',
                  'price',
                  'amount',
                  'image_url')