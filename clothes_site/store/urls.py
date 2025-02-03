from django.urls import path,include
from .views import *

urlpatterns = [
    #default register
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('', ClothesListAPIView.as_view(), name='clothes_list'),

    path('<int:pk>/', ClothesDetailViewSet.as_view(), name='clothes_detail'),

    path('category/', CategoryListAPIView.as_view(), name='category_clothes'),

    path('promo/', PromoCategoryListAPIView.as_view(), name='promo_clothes'),

    path('review_add/', ReviewCreateAPIView.as_view(), name='review_add'),

    path('cart_item/create/', CartItemCreateAPIView.as_view(), name='cart_item_create'),

    path('cart_item/<int:pk>/', CartItemUpdateDeleteApiView.as_view(), name='cart_item_delete'),

    path('cart_item/check/',CartItemListAPIView.as_view(),name = 'cart_item'),

    path('cart/',CartListAPIView.as_view(),name = 'cart_check'),

    path('favorite_item/create/', FavoriteItemCreateViewSet.as_view(), name='favorite_item_create'),

    path('favorite_item/delete/<int:pk>/', FavoriteDeleteAPIView.as_view(), name='favorite_item_delete'),

    path('favorite_item/list/', FavoriteListAPIView.as_view(), name='favorite_item_list'),

    path('profile/', ProfileViewSet.as_view(), name='profile'),

    path('profile/<int:pk>/', UserProfileUpdateViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='profile_detail'),

    path('order/create/', OrderCreateAPIView.as_view(), name='order-list-create'),

    # path('user/order/create/',UserForOrderCreateAPIView.as_view(),name = 'user_for_order'),

    path('order/check/',OrderCheckAPIView.as_view(),name = 'order_check'),

    path('order/detail/<int:pk>/',OrderDeleteAPIView.as_view(),name = 'order_detail'),

    path('photo/',PhotoListAPIView.as_view(),name='photo'),

    path('about_me/',MainAbout_meListAPIView.as_view(),name = 'about_me_list'),

    path('password_reset/verify_code/', verify_reset_code, name='verify_reset_code'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),

    path('pay/',PayListAPIView.as_view(),name = 'pay'),

    path('sale/',SaleListAPIView.as_view(),name = 'sale'),

    path('title/',TitleListAPIView.as_view(),name = 'title_vid'),

    path('contact_info/',ContactInfoListAPIView.as_view(),name = 'contact_info'),

    path('end_title/',EndTitleListAPIView.as_view(),name = 'end_title'),

  ]