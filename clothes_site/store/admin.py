from django.contrib import admin
from .models import *

class PhotoColorInlines(admin.TabularInline):
    model = Photo
    extra = 1


class ColorAdmin(admin.ModelAdmin):
    inlines = [PhotoColorInlines]


class TextileInlines(admin.TabularInline):
    model = Textile
    extra = 1


class ColorPhotoInline(admin.TabularInline):
    model = Photo
    extra = 1

inlines = [ColorPhotoInline]


class ClothesAdmin(admin.ModelAdmin):
    inlines = [TextileInlines,ColorPhotoInline]


admin.site.register(UserProfile)
admin.site.register(CategoryClothes)
admin.site.register(PromoCategory)
admin.site.register(Clothes,ClothesAdmin)
# admin.site.register(Textile)
# admin.site.register(Color)
admin.site.register(Review)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(FavoriteItem)

#color
