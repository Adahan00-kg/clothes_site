from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, viewsets, status,permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from urllib3 import request

from .filters import ClothesFilter
from django.http import JsonResponse
from .models import *
from .serializer import *
#авторизация
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics

from .permission import CheckOwnerOrder
from django.contrib.auth import authenticate


# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
#
# @api_view(['POST'])
# def verify_reset_code(request):
#     serializer = VerifyResetCodeSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response({'message': 'Пароль успешно сброшен.'}, status=status.HTTP_200_OK)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    queryset = Cart.objects.all()
    serializer_class = CartListSerializer

    # def get_queryset(self):
    #     return Cart.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

class CartItemCreateAPIView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    # queryset = CartItem.objects.all()
    # def get_queryset(self):
    #     return CartItem.objects.filter(cart__user=self.request.user)
    #
    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            product = serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response({'detail':f'{e} , маалымат тура эмес берилди '},status = status.HTTP_400_BAD_REQUEST)
        except NameError as e:
            return Response({'detail':f'{e} ,  ошибка в коде '},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except KeyError as e :
            return Response({'detail':f' {e} - ошибка в атрибуте '})
        except Exception :
            return Response({'detail':'сервер не работает'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CartItemUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)


class CartItemListAPIView(generics.ListAPIView):
    serializer_class = CartItemCheckSerializer
    # queryset = CartItem.objects.all()

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

class ClothesDetailViewSet(generics.RetrieveAPIView):
    queryset = Clothes.objects.all()
    serializer_class = ClothesDetailSerializer



class FavoriteItemCreateViewSet(generics.CreateAPIView):
    serializer_class = FavoriteItemCreateSerializer


class FavoriteDeleteAPIView(generics.DestroyAPIView):
    queryset = FavoriteItem.objects.all()
    serializer_class = FavoriteItemALLCheckSerializer

class FavoriteListAPIView(generics.ListAPIView):
    queryset = FavoriteItem.objects.all()
    serializer_class = FavoriteItemALLCheckSerializer


class ProfileViewSet(generics.ListAPIView):
    serializer_class = ProfileCheckSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(id=self.request.user.id)


class UserProfileUpdateViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileUpdateSerializer
    queryset = UserProfile.objects.all()


class PhotoListAPIView(generics.ListAPIView):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    filter_backends =[DjangoFilterBackend]


class MainAbout_meListAPIView(generics.ListAPIView):
    queryset = MainAbout_Me.objects.all()
    serializer_class = MainAbout_meSerializer



class UserForOrderCreateAPIView(generics.ListCreateAPIView):
    queryset = OrderInfoUser.objects.all()
    serializer_class = UserForOrderSerializer



class OrderCreateAPIView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

class OrderCheckAPIView(generics.ListAPIView):
    # queryset = Order.objects.all()
    serializer_class = OrderCheckSerializer

    def get_queryset(self):
        return Order.objects.filter(order_user = self.request.user)


class OrderDeleteAPIView(generics.RetrieveDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCheckSerializer
    permission_classes = [permissions.IsAuthenticated,CheckOwnerOrder]


