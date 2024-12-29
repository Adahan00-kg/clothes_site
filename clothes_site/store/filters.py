from .models import Clothes, Color, Textile
from django_filters import FilterSet


class ClothesFilter(FilterSet):
    class Meta:
        model = Clothes
        fields = {
            'price': ['gt', 'lt'],
            'size': ['gt', 'lt'],
            'category': ['exact'],# Категории (Платья, Хиджабы и т. д.).

        }


class ColorFilter(FilterSet):
    class Meta:
        model = Color
        fields = {
            'color': ['exact']
        }


class TextileFilter(FilterSet):
    class Meta:
        model = Textile
        fields = {
            'textile_name': ['exact']
        }
