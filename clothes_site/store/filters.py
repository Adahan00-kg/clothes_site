from .models import Clothes, Textile, Photo
from django_filters import FilterSet


class ClothesFilter(FilterSet):
    class Meta:
        model = Clothes
        fields = {
            'category': ['exact'],# Категории (Платья, Хиджабы и т. д.).
            'promo_category':['exact'],
        }


