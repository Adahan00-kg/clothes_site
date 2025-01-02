from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, viewsets, status,permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from urllib3 import request

from .filters import ClothesFilter, ColorFilter
from .models import *
from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import *

#авторизация
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from django.contrib.auth import authenticate


# Регистрация
class RegisterView(generics.CreateAPIView):
    serializer_class = UserProfileSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Создаём токены
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        # Устанавливаем токены в cookies
        response.set_cookie(
            key='access_token',
            value=str(access),
            httponly=True,
            secure=True,  # Используйте secure=True для HTTPS
            samesite='Strict',
        )
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite='Strict',
        )
        return response


# Вход
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({"detail": "Неверные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response = Response(serializer.data, status=status.HTTP_200_OK)
        # Устанавливаем токены в cookies
        response.set_cookie(
            key='access_token',
            value=str(access),
            httponly=True,
            secure=True,  # Используйте secure=True для HTTPS
            samesite='Strict',
        )
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite='Strict',
        )
        return response


# Выход
class LogoutView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        try:
            # Получаем refresh токен из cookie
            refresh_token = request.COOKIES.get("refresh_token")
            if not refresh_token:
                return Response({"detail": "Refresh токен отсутствует"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response(status=status.HTTP_205_RESET_CONTENT)
            # Удаляем токены из cookies
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            return response
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


 # cart_cartitem create
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Cart, CartItem, Clothes, Color


# class Cart_addViewSet(viewsets.ModelViewSet):
#     serializer_class = CartListSerializer
#     def add_to_cart(request):
#         clothes_id = request.POST.get('clothes_id')
#         size = request.POST.get('size')
#         color_id = request.POST.get('color_id')
#         quantity = int(request.POST.get('quantity', 1))
#
#         # Получаем одежду и цвет
#         clothes = get_object_or_404(Clothes, id=clothes_id)
#         color = get_object_or_404(Color, id=color_id)
#
#         # Для анонимного пользователя
#         if not request.user.is_authenticated:
#             session_key = request.session.session_key
#             if not session_key:
#                 request.session.create()
#             cart, created = Cart.objects.get_or_create(session_key=session_key, user=None)
#         else:
#             # Для авторизованного пользователя
#             cart, created = Cart.objects.get_or_create(user=request.user)
#
#         # Добавляем товар в корзину
#         cart_item, created = CartItem.objects.get_or_create(
#             cart=cart,
#             clothes=clothes,
#             size=size,
#             color=color
#         )
#         if not created:
#             cart_item.quantity += quantity  # Увеличиваем количество, если уже есть
#             cart_item.save()
#
#         return JsonResponse({'message': 'Товар добавлен в корзину'})

#check cart
class Check_cart(viewsets.ModelViewSet):

    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def view_cart(request):
        if not request.user.is_authenticated:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
            cart = Cart.objects.filter(session_key=session_key).first()
        else:
            cart = Cart.objects.filter(user=request.user).first()

        if not cart:
            return JsonResponse({'message': 'Корзина пуста'})

        items = [
            {
                'clothes_name': item.clothes.clothes_name,
                'size': item.size,
                'color': item.color.color,
                'quantity': item.quantity,
                'total_price': item.get_total_price(),
            }
            for item in cart.cart_items.all()
        ]
        return JsonResponse({'items': items, 'total_price': cart.get_total_price()})

from .models import Order
class OrderCreate(viewsets.ModelViewSet):

    def checkout(request):
        if not request.user.is_authenticated:
            name = request.POST.get('name')
            email = request.POST.get('email')
            address = request.POST.get('address')

            if not name or not email or not address:
                return JsonResponse({'error': 'Необходимо заполнить все поля'})

            # Сохраняем информацию о пользователе в заказ
            user = UserProfile.objects.create(username=email, email=email)
            user.save()
        else:
            user = request.user

        cart = Cart.objects.filter(user=user).first()
        if not cart:
            return JsonResponse({'error': 'Корзина пуста'})

        # Создаём заказ
        order = Order.objects.create(
            order_user=user,
            cart=cart,
            address=request.POST.get('address'),
            payment_method=request.POST.get('payment_method'),
            total_price=cart.get_total_price()
        )

        return JsonResponse({'message': 'Заказ оформлен', 'order_id': order.id})


class ClothesListAPIView(generics.ListAPIView):
    queryset = Clothes.objects.all()
    serializer_class = ClothesListSerializer
    filter_backends = [OrderingFilter,SearchFilter]
    filterset_class = ClothesFilter

class CategoryListAPIView(generics.ListAPIView):
    queryset = CategoryClothes.objects.all()
    serializer_class = CategoryClothesSerializer


class PromoCategoryListAPIView(generics.ListAPIView):
    queryset = PromoCategory.objects.all()
    serializer_class = PromoCategorySerializer


class ReviewCreateAPIView(generics.CreateAPIView):
    serializer_class = ReviewSerializer



class CartListAPIView(generics.ListAPIView):

    serializer_class = CartListSerializer

    def get_queryset(self):
        return Cart.objects.filter(user_id=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)


class CartItemCreateAPIView(generics.CreateAPIView):#?
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)


class CartItemUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)


class ClothesDetailViewSet(generics.RetrieveAPIView):
    queryset = Clothes.objects.all()
    serializer_class = ClothesDetailSerializer


class FavoriteViewSet(generics.ListAPIView):
    serializer_class = FavoriteCheckSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['time']


    def get_queryset(self):
        return Favorite.objects.filter(favorite_user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        favorite, created = Favorite.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(favorite)
        return Response(serializer.data)


class FavoriteItemViewSet(generics.ListCreateAPIView):
    serializer_class = FavoriteItemSerializer

    def perform_create(self, serializer):
        favorite_item, created = FavoriteItem.objects.get_or_create(user=self.request.user)
        serializer.save(favorite=favorite_item)

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileCheckSerializer
    # queryset = UserProfile.objects.all()
    def get_queryset(self):
        return UserProfile.objects.filter(id=self.request.user.id)


class UserProfileUpdateViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileUpdateSerializer


class PhotoListAPIView(generics.ListAPIView):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    filter_backends =[DjangoFilterBackend]
    filterset_class = ColorFilter