from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, OrderItem, ContactMessage,Cart, CartItem, UserProfile
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import ContactForm, UserProfileForm, CustomUserCreationForm

# Create your views here.

def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})

def get_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart

@login_required
def add_to_cart(request, product_id):
    cart = get_cart(request.user)
    product = Product.objects.get(id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.save()

    messages.success(request, "Producto añadido al carrito")
    return redirect('product_list')

@login_required
def view_cart(request):
    cart = get_cart(request.user)
    items = CartItem.objects.filter(cart=cart)

    total = sum(item.product.price * item.quantity for item in items)

    return render(request, 'shop/cart.html', {
        'cart_items': items,
        'total': total
    })

@login_required
def remove_from_cart(request, product_id):
    cart = get_cart(request.user)

    CartItem.objects.filter(
        cart=cart,
        product_id=product_id
    ).delete()

    return redirect('view_cart')

@login_required
def clear_cart(request):
    cart = get_cart(request.user)
    CartItem.objects.filter(cart=cart).delete()

    return redirect('view_cart')

@login_required
def update_cart(request, product_id):
    cart = get_cart(request.user)
    quantity = int(request.POST.get('quantity', 1))

    cart_item = CartItem.objects.get(
        cart=cart,
        product_id=product_id
    )

    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('view_cart')

@login_required
def checkout(request):
    cart = get_cart(request.user)
    items = CartItem.objects.filter(cart=cart)

    if not items:
        return redirect('product_list')

    order = Order.objects.create(user=request.user)

    for item in items:
        product = item.product
        quantity = item.quantity

        #validar stock
        if product.stock < quantity:
            messages.error(
                request,
                f"No hay suficiente stock de {product.name}"
            )
            return redirect('view_cart')

        #restar stock
        product.stock -= quantity
        product.save()

        #crear pedido
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity
        )

    #vaciar carrito
    items.delete()

    messages.success(request, "Pedido realizado correctamente")

    return render(request, 'shop/checkout_success.html', {'order': order})

@login_required
def payment(request):
    cart = get_cart(request.user)
    items = CartItem.objects.filter(cart=cart)

    if not items:
        return redirect('product_list')
    
    #validar datos de usuario obligatorios
    profile = UserProfile.objects.get(user=request.user)

    # VALIDAR DATOS
    if not all([
        profile.name,
        profile.last_name,
        profile.address,
        profile.city,
        profile.postal_code,
        profile.phone
    ]):
        messages.error(request, "Debes completar tu perfil antes de pagar")
        return redirect('profile')

    # validar stock
    for item in items:
        if item.product.stock < item.quantity:
            messages.error(
                request,
                f"No hay suficiente stock de {item.product.name}"
            )
            return redirect('view_cart')

    if request.method == "POST":
        return redirect('checkout')

    return render(request, 'shop/payment.html')

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'shop/register.html', {'form': form})

def search_products(request):
    query = request.GET.get('q')
    results = []

    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, 'shop/search_results.html', {
        'products': results,
        'query': query
    })

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                message=form.cleaned_data['message']
            )

            messages.success(request, "Mensaje enviado correctamente")
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'shop/contact.html', {'form': form})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')

    return render(request, 'shop/order_history.html', {
        'orders': orders
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    return render(request, 'shop/order_detail.html', {
        'order': order
    })

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()

            email = form.cleaned_data.get('email')
            if email:
                request.user.email = email
                request.user.save()

            messages.success(request, "Perfil actualizado correctamente")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
        form.fields['email'].initial = request.user.email

    return render(request, 'shop/profile.html', {'form': form})

def products_by_category(request, category_id):
    products = Product.objects.filter(category_id=category_id)

    return render(request, 'shop/product_list.html', {
        'products': products,
        'selected_category': category_id
    })
