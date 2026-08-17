from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Home
    path('', views.HomeView.as_view(), name='home'),

    # Products
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/category/<slug:category_slug>/', views.ProductListView.as_view(), name='product_list_by_category'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),

    # Cart
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.UpdateCartView.as_view(), name='update_cart'),
    path('cart/remove/<int:item_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/clear/', views.ClearCartView.as_view(), name='clear_cart'),

    # Checkout & Orders
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order/success/', views.OrderSuccessView.as_view(), name='order_success'),
    path('orders/', views.OrderHistoryView.as_view(), name='order_history'),
    path('orders/<str:order_number>/', views.OrderDetailView.as_view(), name='order_detail'),

    # Wishlist
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.ToggleWishlistView.as_view(), name='toggle_wishlist'),
]
