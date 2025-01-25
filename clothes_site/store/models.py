from django.contrib.auth.models import AbstractUser
from django.db import models
from multiselectfield import MultiSelectField
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MaxValueValidator

class UserProfile(AbstractUser):
    number = PhoneNumberField(region='KG')
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.username} - {self.email}'


class CategoryClothes(models.Model):
    category_name = models.CharField(max_length=32)# дублонка , курктка,

    def __str__(self):
        return f'{self.category_name}'


class PromoCategory(models.Model):#акция,хит продаж,тренд,колекция
    promo_category = models.CharField(max_length=32)
    time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.promo_category}'


class Clothes(models.Model):
    clothes_name = models.CharField(max_length=32)# толстовка
    category = models.ManyToManyField(CategoryClothes,  related_name='clothes_category')
    promo_category = models.ManyToManyField(PromoCategory, related_name='clothes_with_promo')
    SIZE_CHOICES = (
        ('XXS', 'XXS'),
        ('XS', 'XS'),
        ('S', 'S'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL')
    )
    size = MultiSelectField(verbose_name='размер', choices=SIZE_CHOICES)
    price = models.PositiveIntegerField(default=0)
    made_in = models.CharField(max_length=32)
    active = models.BooleanField(default=True, verbose_name='в наличии')
    quantities = models.PositiveSmallIntegerField()
    created_date = models.DateField(auto_now_add=True)
    clothes_description = models.TextField(null=True,blank=True)
    clothes_discount = models.PositiveSmallIntegerField(null=True,blank=True,help_text='процент скидки')

    def __str__(self):
        return f'{self.clothes_name} - {self.price}'

    def get_average_rating(self):
        ratings = self.clothes_review.all()
        if ratings.exists():
            average = round(sum(rating.stars for rating in ratings) / ratings.count(), 1)
            return average
        return 0


    def get_discount_price(self):
        if self.clothes_discount:
            discount_multiplier = (100 - self.clothes_discount) / 100
            return round(self.price * discount_multiplier, 2)
        return self.price


class Textile(models.Model):
    textile_name = models.CharField(max_length=35)
    textile_clothes = models.ForeignKey(Clothes, on_delete=models.CASCADE,related_name='textile_clothes')


class Photo(models.Model):
    photo = models.FileField(upload_to='clothes_color_img/')
    clothes_photo = models.ForeignKey(Clothes, on_delete=models.CASCADE, related_name='clothes_img')
    color = models.CharField(max_length=55)

    def __str__(self):
        return f'{self.color} - {self.clothes_photo}'


class Review(models.Model):
    author = models.ForeignKey(UserProfile, related_name='user_review', on_delete=models.CASCADE)
    clothes_review = models.ForeignKey(Clothes, related_name='clothes_review', on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)
    stars = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Рейтинг", null=True, blank=True)
    review_photo = models.ImageField(upload_to='review_img/', null=True, blank=True)
    created_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.author} - {self.clothes_review} - {self.stars}'


class Cart(models.Model):
    user = models.ForeignKey(UserProfile,null=True, blank=True, on_delete=models.SET_NULL,related_name='cart_user')  # Авторизованный пользователь
    session_key = models.CharField(max_length=32, null=True, blank=True)  # Для анонимного пользователя
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Корзина для пользователя: {self.user or "Аноним"}'

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.cart_items.all())



class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    clothes = models.ForeignKey(Clothes, on_delete=models.CASCADE)
    size = models.CharField(max_length=25, choices=Clothes.SIZE_CHOICES)  # Размер
    color = models.ForeignKey(Photo, on_delete=models.CASCADE)  # Цвет
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.clothes} - {self.quantity}'

    def get_total_price(self):
        if self.clothes.clothes_discount is not None:
            discount_multiplier = (100 - self.clothes.clothes_discount) / 100
            total_price = round(self.clothes.price * discount_multiplier, 2)
            return total_price * self.quantity
        return self.clothes.price * self.quantity

    def get_price_clothes(self):
        return self.clothes.price

    def get_just_price(self):
        if self.clothes.clothes_discount is not None:
            discount_multiplier = (100 - self.clothes.clothes_discount) / 100
            return self.clothes.price * discount_multiplier
        else:
            return None




# class OrderInfoUser(models.Model):
#     first_name = models.CharField(max_length=130)
#     phone_number = PhoneNumberField(region='KG')
#     city = models.CharField(max_length=50)
#     address = models.CharField(max_length=55)
#
#
#     def __str__(self):
#         return f'{self.first_name} - {self.phone_number}'

class Pay(models.Model):
    pay_img = models.ImageField(upload_to='pay_img/')
    whatsapp = models.URLField(null=True, blank=True)



class Order(models.Model):
    order_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE,related_name='order_user')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = (
        ('обработка', 'Oбработка'),
        ('заказ собирается','заказ собирается'),
        ('в процессе доставки', 'в процессе доставки'),
        ('доставлен', 'Доставлен'),
        ('отменен', 'Отменен'),

    )
    order_status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='Oбработка')
    STATUS_DELIVERY = (
        ('курьер', 'курьер'),
        ('самовызов', 'самовызов'),
    )
    delivery = models.CharField(max_length=20, default='самовызов', choices=STATUS_DELIVERY)
    # order_info = models.ForeignKey(OrderInfoUser,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=130)
    phone_number = PhoneNumberField(region='KG')
    city = models.CharField(max_length=50)
    address = models.CharField(max_length=55)



    def __str__(self):
        return f'{self.order_user} - {self.first_name} - {self.cart}'



#считает общую стоимость всех товаров в корзине и сохраняет её в заказы короче



class FavoriteItem(models.Model):
    favorite_user = models.ForeignKey(UserProfile,on_delete=models.CASCADE,related_name='favorite')
    clothes = models.ForeignKey(Clothes, on_delete=models.CASCADE, related_name='clothes_favorite')
    time = models.DateTimeField(auto_now_add=True)
    like = models.BooleanField(default=False)


    def __str__(self):
        return f'{self.favorite_user} - {self.clothes}'



class MainAbout_Me(models.Model):
    title = models.CharField(max_length=150)
    made = models.CharField(max_length=150)
    logo = models.ImageField(upload_to='about_me/')

    def __str__(self):
        return f'{self.title}'


class About_me(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField(null=True,blank=True)
    img = models.ImageField(upload_to='img_about_me')
    connect = models.ForeignKey(MainAbout_Me,on_delete=models.CASCADE,related_name='about_me')

    def __str__(self):
        return f'{self.title}'



class Sale(models.Model):
    img = models.ImageField(upload_to='sale_img/')
    title = models.CharField(max_length=100,null=True,blank=True)
    text = models.TextField(null=True,blank=True)

    def __str__(self):
        return f'{self.title}'


class TitleVid(models.Model):
    made = models.CharField(max_length=100)
    title = models.CharField(max_length=250)
    img1 = models.ImageField(upload_to='title_img/')
    img2 = models.ImageField(upload_to='title_img/')
    img3 = models.ImageField(upload_to='title_img/')

    def __str__(self):
        return f'{self.title}'


class ContactInfo(models.Model):
    messenger = models.CharField(max_length=100,null=True,blank=True)
    email = models.CharField(max_length=100,null=True,blank=True)
    address = models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return f'{self.messenger}'


