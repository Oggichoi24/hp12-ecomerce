from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),                            # thiếu
    path("register/", views.register_view, name="register"),
    path('add/', views.add_laptop, name="laptop"),
    path('delete/<int:laptop_id>/', views.delete_laptop, name="delete_laptop"),   # thiếu
    path("cart/", views.get_cart, name="cart"),
    path("cart/add/", views.add_to_cart, name="add_to_cart"),                     # thiếu
    path("cart/update/<int:item_id>/", views.update_cart_item, name="update_cart_item"),  # thiếu
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),  # thiếu
    path("cart/clear/", views.clear_cart, name="clear_cart"),                     # thiếu
]