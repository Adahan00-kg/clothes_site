from .models import *

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
# from django_rest_passwordreset.models import ResetPasswordTokend


class UserProfileSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model = UserProfile
        fields = ['username', 'email','password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        # Проверка на совпадение паролей
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})

        # Валидация пароля через встроенные проверки Django
        validate_password(attrs['password'])

        return attrs

    def create(self, validated_data):
        # Удаляем confirm_password из данных перед созданием пользователя
        validated_data.pop('confirm_password')
        user = UserProfile.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }




# class VerifyResetCodeSerializer(serializers.Serializer):
#     email = serializers.EmailField()  # Email пользователя
#     reset_code = serializers.IntegerField()  # 4-значный код
#     new_password = serializers.CharField(write_only=True)  # Новый пароль
#
#     def validate(self, data):
#         email = data.get('email')
#         reset_code = data.get('reset_code')
#
#         # Проверяем, существует ли указанный код для email
#         try:
#             token = ResetPasswordToken.objects.get(user__email=email, key=reset_code)
#         except ResetPasswordToken.DoesNotExist:
#             raise serializers.ValidationError("Неверный код сброса или email.")
#
#         data['user'] = token.user
#         return data
#
#     def save(self):
#         user = self.validated_data['user']
#         new_password = self.validated_data['new_password']
#
#         # Устанавливаем новый пароль
#         user.set_password(new_password)
#         user.save()
#


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return {'user': user}  # Возвращаем объект пользователя
        raise serializers.ValidationError("Неверные учетные данные")

    def to_representation(self, instance):
        user = instance['user']
        refresh = RefreshToken.for_user(user)
        return {
            'user': {
                'username': user.username,
                'email': user.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['username', 'first_name', 'last_name', 'address', 'index_pochta','number']


class UserProfileSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name']


class PromoCategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCategory
        fields = ['promo_category']


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'photo', 'color']


class ClothesListSerializer(serializers.ModelSerializer):
    promo_category = PromoCategorySimpleSerializer(many=True)
    average_rating = serializers.SerializerMethodField()
    # created_date = serializers.DateField(format('%d%m%Y'))
    discount_price = serializers.SerializerMethodField()
    clothes_img = PhotoSerializer(read_only=True, many=True)
    class Meta:
        model = Clothes
        fields = ['id', 'promo_category', 'clothes_name',
                  'price','discount_price', 'size', 'average_rating','created_date','clothes_img']

    def get_average_rating(self,obj):
        return obj.get_average_rating()

    def get_discount_price(self,obj):
        return obj.get_discount_price()


class CategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryClothes
        fields = ['category_name']


class CategoryClothesSerializer(serializers.ModelSerializer):
    clothes_category = ClothesListSerializer(many=True)
    class Meta:
        model = CategoryClothes
        fields = ['category_name', 'clothes_category']


class PromoSimpleSerializer(serializers.ModelSerializer):
    time = serializers.DateTimeField(format('%h-%m-%Y  %H:%M'))

    class Meta:
        model = PromoCategory
        fields =['promo_category', 'time']


class PromoCategorySerializer(serializers.ModelSerializer):
    clothes_with_promo = ClothesListSerializer(many=True)

    class Meta:
        model = PromoCategory
        fields = ['promo_category', 'time', 'clothes_with_promo']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['author', 'text', 'stars', 'review_photo', 'clothes_review']


class ReviewReadSerializer(serializers.ModelSerializer):
    author = UserProfileSimpleSerializer()
    created_date = serializers.DateTimeField(format('%d-%m-%Y  %H:%M'))

    class Meta:
        model = Review
        fields = ['author', 'text', 'stars', 'review_photo', 'created_date']

class ClothesForCartSerializer(serializers.ModelSerializer):
    clothes_img = PhotoSerializer(read_only=True, many=True)
    class Meta:
        model  = Clothes
        fields= ['clothes_name','clothes_img']


class CartItemSerializer(serializers.ModelSerializer):
    clothes = ClothesForCartSerializer(read_only=True)
    clothes_id = serializers.PrimaryKeyRelatedField(queryset=Clothes.objects.all(), write_only=True, source='clothes')
    color = PhotoSerializer(read_only=True)
    color_id = serializers.PrimaryKeyRelatedField(queryset=Photo.objects.all(), write_only=True, source='color')
    class Meta:
        model = CartItem
        fields = ['id','clothes', 'clothes_id', 'quantity', 'size', 'color','color_id']


class CartItemCheckSerializer(serializers.ModelSerializer):
    clothes = ClothesForCartSerializer(read_only=True)
    price_clothes = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    clothes_id = serializers.PrimaryKeyRelatedField(queryset=Clothes.objects.all(), write_only=True, source='clothes')
    color_id = serializers.PrimaryKeyRelatedField(queryset=Photo.objects.all(), write_only=True, source='color')
    class Meta:
        model = CartItem
        fields = ['id','clothes','size','color','quantity','price_clothes','total_price','color_id','clothes_id']

    def get_price_clothes(self,obj):
        return obj.get_price_clothes()

    def get_total_price(self,obj):
        return obj.get_total_price()


class CartListSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    cart_items = CartItemCheckSerializer(many=True,read_only=True)
    class Meta:
        model = Cart
        fields = ['id', 'user', 'total_price','cart_items']

    def get_total_price(self, obj):
        return obj.get_total_price()




class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_user', 'cart', 'date',
                  'delivery', 'address', 'payment_method']




class TextileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Textile
        fields = ['textile_name']


class ClothesDetailSerializer(serializers.ModelSerializer):
    category = CategorySimpleSerializer(many=True)
    promo_category = PromoSimpleSerializer(many=True)
    clothes_img  = PhotoSerializer(read_only=True,many=True)
    clothes_review = ReviewReadSerializer(many=True)
    average_rating = serializers.SerializerMethodField()
    textile_clothes = TextileSerializer(read_only=True, many=True)
    discount_price = serializers.SerializerMethodField()
    class Meta:
        model = Clothes
        fields = ['id','clothes_name', 'category',
                  'promo_category', 'quantities', 'active', 'price','discount_price', 'size', 'average_rating',
                  'made_in', 'textile_clothes', 'clothes_img', 'clothes_review','clothes_description']


    def get_average_rating(self, obj):
        return obj.get_average_rating()

    def get_discount_price(self,obj):
        return obj.get_discount_price()



# class FavoriteItemCreateSerializer(serializers.ModelSerializer):
#     clothes_id = serializers.PrimaryKeyRelatedField(queryset=Clothes.objects.all(), write_only=True, source='clothes')
#     clothes = ClothesListSerializer()
#     class Meta:
#         model = FavoriteItem
#         fields = ['clothes','clothes_id']

class FavoriteItemCreateSerializer(serializers.ModelSerializer):
    clothes_id = serializers.PrimaryKeyRelatedField(queryset=Clothes.objects.all(), write_only=True, source='clothes')
    clothes = ClothesListSerializer(read_only=True)

    class Meta:
        model = FavoriteItem
        fields = ['id', 'clothes', 'clothes_id','favorite_user']

class FavoriteItemALLCheckSerializer(serializers.ModelSerializer):
    clothes = ClothesListSerializer()
    time = serializers.DateTimeField(format('%d - %m %Y  %H:%M'))
    class Meta:
        model = FavoriteItem
        fields= ['id','clothes','time']


# class FavoriteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Favorite
#         fields = ['favorite_user', 'created_date']
#
#
# class FavoriteItemSerializer(serializers.ModelSerializer):
#     clothes_id = serializers.PrimaryKeyRelatedField(queryset=Clothes.objects.all(), write_only=True, source='clothes')
#     class Meta:
#         model = FavoriteItem
#         fields = ['clothes','clothes_id']
#
# class FavoriteItemCheckSerializer(serializers.ModelSerializer):
#     clothes_id = serializers.PrimaryKeyRelatedField(queryset=Clothes.objects.all(), write_only=True, source='clothes')
#     class Meta:
#         model = FavoriteItem
#         fields = ['clothes','clothes_id','time']





class ProfileCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id','username','first_name','last_name',
                  'number','address','index_pochta',]


