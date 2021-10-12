from django.conf.urls import url
from Product import views

urlpatterns = [
    url(r'^infos/products$', views.product_list),
    url(r'^infos/products/(?P<pk>[0-9]+)$', views.product_detail),
]