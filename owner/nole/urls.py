
Copy

from django.urls import path
from . import views
 
urlpatterns = [
    # ── Home & Auth ──────────────────────────────────────────────
    path('',                        views.home),
    path('login/',                  views.login_view,      name='login'),
    path('logout/',                 views.logout_view,     name='logout'),
    path('register/',               views.register_view,   name='register'),
 
    # ── Admin Dashboard ──────────────────────────────────────────
    path('admin-dashboard/',        views.admin_dashboard,   name='admin_dashboard'),
 
    # ── Admin: Laptop ────────────────────────────────────────────
    path('admin-dashboard/laptops/',                          views.admin_laptop_list, name='admin_laptop_list'),
    path('admin-dashboard/laptops/edit/<int:laptop_id>/',     views.edit_laptop,       name='edit_laptop'),
    path('add/',                                              views.add_laptop,        name='laptop'),
    path('delete/<int:laptop_id>/',                           views.delete_laptop,     name='delete_laptop'),
 
    # ── Admin: Orders ────────────────────────────────────────────
    path('admin-dashboard/orders/',                           views.admin_order_list,   name='admin_order_list'),
    path('admin-dashboard/orders/<int:order_id>/',            views.admin_order_detail, name='admin_order_detail'),
 
    # ── Cart ─────────────────────────────────────────────────────
    path('cart/',                   views.get_cart,          name='cart'),
    path('cart/add/',               views.add_to_cart,       name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/',             views.clear_cart,        name='clear_cart'),
 
    # ── Orders (khách hàng) ───────────────────────────────────────
    path('checkout/',               views.checkout,         name='checkout'),
    path('orders/',                 views.order_list,       name='order_list'),
    path('orders/<int:order_id>/',  views.order_detail,     name='order_detail'),
    path('orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
]
 