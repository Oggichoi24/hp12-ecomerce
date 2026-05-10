from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Laptop, Cart, CartItem
import json


# ==================== AUTH ====================

def home(request):
    laptops = Laptop.objects.all()
    return render(request, "home.html", {"products": laptops})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("/")
        messages.error(request, "Sai tài khoản hoặc mật khẩu")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("/login/")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        username = request.POST.get("username")
        email    = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Tên đăng nhập đã tồn tại")
            return render(request, "register.html")

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Đăng ký thành công, hãy đăng nhập")
        return redirect("/login/")

    return render(request, "register.html")


# ==================== LAPTOP ====================

@login_required
def add_laptop(request):
    if request.method == "POST":
        Laptop.objects.create(
            name    = request.POST.get("name"),
            brand   = request.POST.get("brand"),
            cpu     = request.POST.get("cpu"),
            ram     = request.POST.get("ram"),
            storage = request.POST.get("storage"),
            price   = request.POST.get("price")
        )
        messages.success(request, "Đã thêm laptop thành công")
        return redirect("/")

    return render(request, "add_laptop.html")


@login_required
def delete_laptop(request, laptop_id):
    laptop = get_object_or_404(Laptop, id=laptop_id)
    laptop.delete()
    messages.success(request, "Đã xóa laptop")
    return redirect("/")


# ==================== CART ====================

@login_required
def get_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, "cart.html", {"cart": cart})


@login_required
@require_http_methods(["POST"])
def add_to_cart(request):
    data   = json.loads(request.body)
    laptop = get_object_or_404(Laptop, id=data.get("laptop_id"))
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, laptop=laptop)
    item.quantity = item.quantity + data.get("quantity", 1) if not created else data.get("quantity", 1)
    item.save()
    return JsonResponse({"message": "Đã thêm vào giỏ hàng", "quantity": item.quantity})


@login_required
@require_http_methods(["PUT"])
def update_cart_item(request, item_id):
    data     = json.loads(request.body)
    item     = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = data.get("quantity", 1)
    if quantity <= 0:
        item.delete()
        return JsonResponse({"message": "Đã xóa sản phẩm"})
    item.quantity = quantity
    item.save()
    return JsonResponse({"message": "Đã cập nhật", "quantity": item.quantity})


@login_required
@require_http_methods(["DELETE"])
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return JsonResponse({"message": "Đã xóa sản phẩm"})


@login_required
@require_http_methods(["DELETE"])
def clear_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()
    return JsonResponse({"message": "Đã xóa giỏ hàng"})