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
admin.site.register(MainAbout_Me)
admin.site.register(About_me)
# admin.site.register(OrderInfoUser)
admin.site.register(Pay)
admin.site.register(Sale)
admin.site.register(TitleVid)
admin.site.register(ContactInfo)
admin.site.register(EndTitle)
admin.site.register(PayTitle)

#color
