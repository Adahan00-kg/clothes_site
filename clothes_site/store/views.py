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


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['POST'])
def verify_reset_code(request):
    serializer = VerifyResetCodeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Пароль успешно сброшен.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Регистрация
class RegisterView(generics.CreateAPIView):
    serializer_class = UserProfileSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
        except serializers.ValidationError as e:
            return Response ({'detail':f'Маалымат тура эмес келди {e}'})
        except Exception as e:
            return Response({'detail':f'ошибка сервера {e}'})


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
        serializer.is_valid(raise_exception=True)


        user = serializer.validated_data
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
        except Exception :
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'detail':'не правильный ключ'},status.HTTP_400_BAD_REQUEST)






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

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser

# class ReviewAddView(APIView):
#     parser_classes = [MultiPartParser, FormParser]
#
#     @swagger_auto_schema(
#         operation_description="Добавить отзыв",
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             properties={
#                 'author': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID автора'),
#                 'text': openapi.Schema(type=openapi.TYPE_STRING, description='Текст отзыва'),
#                 'stars': openapi.Schema(type=openapi.TYPE_INTEGER, description='Рейтинг (1-5)'),
#                 'review_photo': openapi.Schema(type=openapi.TYPE_FILE, description='Фотография'),
#                 'clothes_review': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID одежды'),
#             },
#             required=['author', 'text', 'stars', 'clothes_review'],
#         ),
#         responses={
#             201: "Отзыв успешно добавлен",
#             400: "Ошибка валидации",
#         },
#     )
#     def post(self, request, *args, **kwargs):
#         serializer = ReviewSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# from drf_yasg import openapi
# from drf_yasg.utils import swagger_auto_schema
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
#
# class ReviewAddView(APIView):
#     parser_classes = [MultiPartParser, FormParser]
#
#     @swagger_auto_schema(
#         operation_description="Добавить отзыв",
#         manual_parameters=[
#             openapi.Parameter(
#                 'author',
#                 openapi.IN_FORM,
#                 description='ID автора',
#                 type=openapi.TYPE_INTEGER,
#                 required=True,
#             ),
#             openapi.Parameter(
#                 'text',
#                 openapi.IN_FORM,
#                 description='Текст отзыва',
#                 type=openapi.TYPE_STRING,
#                 required=True,
#             ),
#             openapi.Parameter(
#                 'stars',
#                 openapi.IN_FORM,
#                 description='Рейтинг (0-5)',
#                 type=openapi.TYPE_INTEGER,
#                 required=True,
#             ),
#             openapi.Parameter(
#                 'review_photo',
#                 openapi.IN_FORM,
#                 description='Фотография',
#                 type=openapi.TYPE_FILE,
#                 required=False,
#             ),
#             openapi.Parameter(
#                 'clothes_review',
#                 openapi.IN_FORM,
#                 description='ID одежды',
#                 type=openapi.TYPE_INTEGER,
#                 required=True,
#             ),
#         ],
#         responses={
#             201: "Отзыв успешно добавлен",
#             400: "Ошибка валидации",
#         },
#     )
#     def post(self, request, *args, **kwargs):
#         serializer = ReviewSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartListAPIView(generics.ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartListSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

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



    # def create(self, request, *args, **kwargs):
    #     # try:
    #         serializer = self.get_serializer(data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         product = serializer.save()
    #         return Response(serializer.data,status=status.HTTP_201_CREATED)
    #     # except serializers.ValidationError as e:
        #     return Response({'detail':f'{e} , маалымат тура эмес берилди '},status = status.HTTP_400_BAD_REQUEST)
        # except NameError as e:
        #     return Response({'detail':f'{e} ,  ошибка в коде '},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # except KeyError as e :
        #     return Response({'detail':f' {e} - ошибка в атрибуте '})
        # except Exception :
        #     return Response({'detail':'сервер не работает'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CartItemUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)


    # def update(self, request, *args, **kwargs):
    #     try:
    #         partial = kwargs.pop('partial', False)
    #         instance = self.get_object()
    #         serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #         serializer.is_valid(raise_exception=True)
    #     except serializers.ValidationError as e:
    #         return Response({'detail':f'тура эмес маалымат {e}'},status.HTTP_400_BAD_REQUEST)
    #     except NameError as e:
    #         return Response({'detail':f'ошибка в коде {e}'},status.HTTP_500_INTERNAL_SERVER_ERROR)
    #     except Exception as e:
    #         return Response({'detail': f'ошибка в коде {e}'}, status.HTTP_500_INTERNAL_SERVER_ERROR)




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
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(id=self.request.user.id)


class UserProfileUpdateViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = UserProfile.objects.all()


class PhotoListAPIView(generics.ListAPIView):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    filter_backends =[DjangoFilterBackend]


class MainAbout_meListAPIView(generics.ListAPIView):
    queryset = MainAbout_Me.objects.all()
    serializer_class = MainAbout_meSerializer







class OrderCreateAPIView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    # permission_classes = [permissions.IsAuthenticated]

class OrderCheckAPIView(generics.ListAPIView):
    # queryset = Order.objects.all()
    serializer_class = OrderCheckSerializer


    def get_queryset(self):
        return Order.objects.filter(order_user = self.request.user)


class OrderDeleteAPIView(generics.RetrieveDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCheckSerializer
    permission_classes = [permissions.IsAuthenticated,CheckOwnerOrder]


class PayListAPIView(generics.ListAPIView):
    queryset = Pay.objects.all()
    serializer_class = PaySerializer



class SaleListAPIView(generics.ListAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer


class TitleListAPIView(generics.ListAPIView):
    queryset = TitleVid.objects.all()
    serializer_class = TitleSerializer


class ContactInfoListAPIView(generics.ListAPIView):
    queryset = ContactInfo.objects.all()
    serializer_class = ContactInfoSerializer



class EndTitleListAPIView(generics.ListAPIView):
    queryset = EndTitle.objects.all()
    serializer_class = EndTitleSerializer

