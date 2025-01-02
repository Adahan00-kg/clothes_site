from .models import Clothes, Color, Textile, Photo
from django_filters import FilterSet


class ClothesFilter(FilterSet):
    class Meta:
        model = Clothes
        fields = {
            'category': ['exact'],# Категории (Платья, Хиджабы и т. д.).
            'promo_category':['exact'],
            'color':['exact'],
        }


class ColorFilter(FilterSet):
    class Meta:
        model = Photo
        fields = {
            'color_connect': ['exact'],
        }