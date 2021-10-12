from django.db import models

# Create your models here.
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=256, null=False)
    image_url = models.CharField(max_length=1024)
    category = models.CharField(max_length=32, null=False, default='')
    price = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)