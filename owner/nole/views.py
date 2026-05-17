from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Laptop, Cart, CartItem, Order, OrderItem
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
 
 
# ==================== ADMIN ====================
 
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect("/")
    return render(request, "admin_dashboard.html")
 
 
@login_required
def admin_laptop_list(request):
    if not request.user.is_staff:
        return redirect("/")
    laptops = Laptop.objects.all()
    return render(request, "admin_laptops.html", {"laptops": laptops})
 
 
# ==================== LAPTOP ====================
 
@login_required
def add_laptop(request):
    if not request.user.is_staff:
        return redirect("/")
    if request.method == "POST":
        Laptop.objects.create(
            name      = request.POST.get("name"),
            brand     = request.POST.get("brand"),
            cpu       = request.POST.get("cpu"),
            ram       = request.POST.get("ram"),
            storage   = request.POST.get("storage"),
            price     = request.POST.get("price"),
            image_url = request.POST.get("image_url")
        )
        messages.success(request, "Đã thêm laptop thành công")
        return redirect("/admin-dashboard/laptops/")
    return render(request, "add_laptop.html")
 
 
@login_required
def edit_laptop(request, laptop_id):
    if not request.user.is_staff:
        return redirect("/")
    laptop = get_object_or_404(Laptop, id=laptop_id)
    if request.method == "POST":
        laptop.name      = request.POST.get("name")
        laptop.brand     = request.POST.get("brand")
        laptop.cpu       = request.POST.get("cpu")
        laptop.ram       = request.POST.get("ram")
        laptop.storage   = request.POST.get("storage")
        laptop.price     = request.POST.get("price")
        laptop.image_url = request.POST.get("image_url")
        laptop.save()
        messages.success(request, "Đã cập nhật thông tin laptop")
        return redirect("/admin-dashboard/laptops/")
    return render(request, "edit_laptop.html", {"laptop": laptop})
 
 
@login_required
def delete_laptop(request, laptop_id):
    if not request.user.is_staff:
        return redirect("/")
    laptop = get_object_or_404(Laptop, id=laptop_id)
    laptop.delete()
    messages.success(request, "Đã xóa laptop")
    return redirect("/admin-dashboard/laptops/")
 
 
# ==================== CART ====================
 
@login_required
def get_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, "cart.html", {"cart": cart})
 
 
@login_required
@require_http_methods(["POST"])
def add_to_cart(request):
    data    = json.loads(request.body)
    laptop  = get_object_or_404(Laptop, id=data.get("laptop_id"))
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
 
 
# ==================== ORDER (KHÁCH HÀNG) ====================
 
@login_required
def checkout(request):
    """Trang checkout: điền thông tin giao hàng và đặt hàng"""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('laptop').all()
 
    if not cart_items.exists():
        messages.error(request, "Giỏ hàng của bạn đang trống!")
        return redirect("/cart/")
 
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        phone     = request.POST.get("phone", "").strip()
        address   = request.POST.get("address", "").strip()
        note      = request.POST.get("note", "").strip()
 
        if not full_name or not phone or not address:
            messages.error(request, "Vui lòng điền đầy đủ thông tin giao hàng")
            return render(request, "checkout.html", {"cart": cart})
 
        # Tạo đơn hàng
        order = Order.objects.create(
            user      = request.user,
            full_name = full_name,
            phone     = phone,
            address   = address,
            note      = note,
            status    = 'PENDING',
        )
 
        # Chuyển CartItem → OrderItem, lưu giá tại thời điểm đặt
        for item in cart_items:
            OrderItem.objects.create(
                order    = order,
                laptop   = item.laptop,
                quantity = item.quantity,
                price    = item.laptop.price,
            )
 
        # Tính tổng và lưu
        order.calculate_total()
 
        # Xóa giỏ hàng
        cart.items.all().delete()
 
        messages.success(request, f"Đặt hàng thành công! Mã đơn hàng #{order.id}")
        return redirect(f"/orders/{order.id}/")
 
    return render(request, "checkout.html", {"cart": cart})
 
 
@login_required
def order_list(request):
    """Lịch sử đơn hàng của khách hàng"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__laptop')
    return render(request, "order_list.html", {"orders": orders})
 
 
@login_required
def order_detail(request, order_id):
    """Chi tiết một đơn hàng của khách hàng"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "order_detail.html", {"order": order})
 
 
@login_required
def cancel_order(request, order_id):
    """Khách hàng hủy đơn - chỉ được hủy khi PENDING"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'PENDING':
        order.status = 'CANCELLED'
        order.save()
        messages.success(request, "Đã hủy đơn hàng thành công")
    else:
        messages.error(request, "Không thể hủy đơn hàng ở trạng thái này")
    return redirect(f"/orders/{order.id}/")
 
 
# ==================== ORDER (ADMIN) ====================
 
@login_required
def admin_order_list(request):
    """Admin xem tất cả đơn hàng"""
    if not request.user.is_staff:
        return redirect("/")
 
    status_filter = request.GET.get("status", "")
    orders = Order.objects.select_related('user').prefetch_related('items__laptop')
    if status_filter:
        orders = orders.filter(status=status_filter)
 
    status_choices = Order.STATUS_CHOICES
    counts = {
        'all':       Order.objects.count(),
        'PENDING':   Order.objects.filter(status='PENDING').count(),
        'CONFIRMED': Order.objects.filter(status='CONFIRMED').count(),
        'SHIPPING':  Order.objects.filter(status='SHIPPING').count(),
        'DELIVERED': Order.objects.filter(status='DELIVERED').count(),
        'CANCELLED': Order.objects.filter(status='CANCELLED').count(),
    }
 
    return render(request, "admin_orders.html", {
        "orders":         orders,
        "status_filter":  status_filter,
        "status_choices": status_choices,
        "counts":         counts,
    })
 
 
@login_required
def admin_order_detail(request, order_id):
    """Admin xem chi tiết + cập nhật trạng thái đơn hàng"""
    if not request.user.is_staff:
        return redirect("/")
 
    order = get_object_or_404(Order, id=order_id)
 
    if request.method == "POST":
        new_status = request.POST.get("status")
        valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
        if new_status in valid_statuses:
            old_status = order.get_status_display()
            order.status = new_status
            order.save()
            messages.success(
                request,
                f"Đã cập nhật đơn #{order.id}: {old_status} → {order.get_status_display()}"
            )
        return redirect(f"/admin-dashboard/orders/{order.id}/")
 
    return render(request, "admin_order_detail.html", {
        "order":          order,
        "status_choices": Order.STATUS_CHOICES,
    })
 