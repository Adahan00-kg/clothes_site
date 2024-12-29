from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, viewsets, status,permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import *
from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import *

#cookie


from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta

class CustomLoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Получаем пользователя из validated_data
        user = serializer.validated_data['']
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({
            'detail': 'Успешный вход',
            'access': access_token,
            'refresh': refresh_token,
        }, status=status.HTTP_200_OK)

        # Устанавливаем токены в cookies
        response.set_cookie(
            key='access',
            value=access_token,
            httponly=True,  # Защищённая cookie, недоступна из JS
            secure=True,    # Используйте True для HTTPS (рекомендуется в продакшене)
            samesite='Lax', # Ограничивает использование кросс-доменных запросов
            max_age=3600    # Время жизни токена (в секундах)
        )
        response.set_cookie(
            key='refresh',
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=timedelta(days=7).total_seconds()
        )

        return response

class LogoutCookieView(APIView):
    def post(self, request):
        response = Response({"detail": "Успешный выход"}, status=status.HTTP_205_RESET_CONTENT)

        # Удаляем cookies
        response.delete_cookie('access')
        response.delete_cookie('refresh')

        return response

class TokenRefreshView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh')
        if not refresh_token:
            return Response({"detail": "Refresh token отсутствует"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response = Response({
                'detail': 'Access token обновлён',
                'access': access_token,
            }, status=status.HTTP_200_OK)

            # Обновляем access token в cookies
            response.set_cookie(
                key='access',
                value=access_token,
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=3600
            )

            return response

        except Exception:
            return Response({"detail": "Недействительный refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

#авторизация
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken



class RegisterView(generics.CreateAPIView):
    serializer_class = UserProfileSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({"detail": "Неверные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

 # cart_cartitem create
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Cart, CartItem, Clothes, Color


class Cart_addViewSet(viewsets.ModelViewSet):
    serializer_class = CartListSerializer
    def add_to_cart(request):
        clothes_id = request.POST.get('clothes_id')
        size = request.POST.get('size')
        color_id = request.POST.get('color_id')
        quantity = int(request.POST.get('quantity', 1))

        # Получаем одежду и цвет
        clothes = get_object_or_404(Clothes, id=clothes_id)
        color = get_object_or_404(Color, id=color_id)

        # Для анонимного пользователя
        if not request.user.is_authenticated:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
            cart, created = Cart.objects.get_or_create(session_key=session_key, user=None)
        else:
            # Для авторизованного пользователя
            cart, created = Cart.objects.get_or_create(user=request.user)

        # Добавляем товар в корзину
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            clothes=clothes,
            size=size,
            color=color
        )
        if not created:
            cart_item.quantity += quantity  # Увеличиваем количество, если уже есть
            cart_item.save()

        return JsonResponse({'message': 'Товар добавлен в корзину'})

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


#
# class AddToCartView(APIView):
#
#     def post(self, request, clothes_id):
#         size = request.data.get('size')  # Получаем выбранный размер
#         color_id = request.data.get('color')  # Получаем выбранный цвет
#
#         if not size or not color_id:
#             return Response({"detail": "Size and color must be selected."}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             color = Color.objects.get(id=color_id)
#             clothes = Clothes.objects.get(id=clothes_id)
#         except (Color.DoesNotExist, Clothes.DoesNotExist):
#             return Response({"detail": "Invalid color or clothes ID."}, status=status.HTTP_404_NOT_FOUND)
#
#         cart, created = Cart.objects.get_or_create(user=request.user)
#         CartItem.objects.create(cart=cart, product=clothes, size=size, color=color)
#
#         return Response({"detail": "Item added to cart."}, status=status.HTTP_201_CREATED)

#
#
# class CreateOrderView(APIView):
#     def post(self, request):
#         try:
#             user = request.user
#             address = request.data.get('address', '')
#             delivery = request.data.get('delivery', 'самовызов')
#
#             if not address:
#                 return Response({"detail": "Address is required."}, status=status.HTTP_400_BAD_REQUEST)
#
#             # Создаем заказ
#             order = Order.objects.create(order_user=user, address=address, delivery=delivery)
#             return Response({"detail": "Order created successfully."}, status=status.HTTP_201_CREATED)
#         except ValidationError as e:
#             return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"detail": "An error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#

# class OrderListCreateView(generics.ListCreateAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]
#
#     def perform_create(self, serializer):
#         serializer.save(order_user=self.request.user)
#             # Устанавливаем текущего пользователя как владельца заказа
#

# class OrderDetailViewSet(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#
#     def get_queryset(self):
#         return Order.objects.filter(order_user=self.request.user)



class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileAllSerializer

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.queryset.user)


class ClothesListAPIView(generics.ListAPIView):
    queryset = Clothes.objects.all()
    serializer_class = ClothesListSerializer
    filter_backends = [OrderingFilter]
    search_fields = ['clothes_name']

class CategoryListAPIView(generics.ListAPIView):
    queryset = CategoryClothes.objects.all()
    serializer_class = CategoryClothesSerializer


class PromoCategoryListAPIView(generics.ListAPIView):
    queryset = PromoCategory.objects.all()
    serializer_class = PromoCategorySerializer


class ReviewCreateAPIView(generics.CreateAPIView):
    serializer_class = ReviewSerializer


class CartCreateAPIView(generics.CreateAPIView):
    serializer_class = CartSimpleSerializer


class CartListAPIView(generics.ListAPIView):

    serializer_class = CartListSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

#     def retrieve(self, request, *args, **kwargs):
#         cart, created = Cart.objects.get_or_create(user=request.user)
#         serializer = self.get_serializer(cart)
#         return Response(serializer.data)
#

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
    search_fields = ['clothes_name']
    ordering_fields = ['price']


class FavoriteViewSet(generics.ListCreateAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class FavoriteItemViewSet(generics.ListCreateAPIView):
    queryset = FavoriteItem.objects.all()
    serializer_class = FavoriteItemSerializer
