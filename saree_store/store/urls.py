from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    
    # AJAX Endpoints
    path('ajax/cart/add/', views.ajax_cart_add, name='ajax_cart_add'),
    path('ajax/cart/update/', views.ajax_cart_update, name='ajax_cart_update'),
    path('ajax/cart/remove/', views.ajax_cart_remove, name='ajax_cart_remove'),
    path('ajax/wishlist/toggle/', views.ajax_wishlist_toggle, name='ajax_wishlist_toggle'),
    path('ajax/product/modal/<slug:slug>/', views.ajax_product_modal, name='ajax_product_modal'),

    
    # Auth Endpoints
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/profile/', views.profile_view, name='profile'),
]
