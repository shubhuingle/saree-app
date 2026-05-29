import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.db.models import Q
from .models import Category, Product, ProductImage, Cart, CartItem, Wishlist, Order, OrderItem, HomeBanner

# Helper helper to get or create cart
def _get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        # Merge session cart to user cart if exists
        session_cart = Cart.objects.filter(session_key=session_key).first()
        if session_cart and session_cart != cart:
            for item in session_cart.items.all():
                user_item, item_created = CartItem.objects.get_or_create(cart=cart, product=item.product)
                if not item_created:
                    user_item.quantity += item.quantity
                user_item.save()
            session_cart.delete()
    else:
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def home(request):
    banners = HomeBanner.objects.filter(is_active=True)
    categories = Category.objects.all()[:6]
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:4]
    
    context = {
        'banners': banners,
        'categories': categories,
        'featured_products': featured_products,
        'latest_products': latest_products,
    }
    return render(request, 'store/home.html', context)

def product_list(request):
    category_slug = request.GET.get('category')
    sort_by = request.GET.get('sort', 'newest')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search_query = request.GET.get('search')

    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    if search_query:
        products = products.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        products = products.filter(is_featured=True)
    else:
        products = products.order_by('-created_at')

    # AJAX filtering support
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('store/includes/product_grid.html', {'products': products, 'request': request})
        return JsonResponse({'html': html})

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_slug,
        'sort_by': sort_by,
    }
    return render(request, 'store/products.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
    
    # Check if in wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    elif request.session.session_key:
        in_wishlist = Wishlist.objects.filter(session_key=request.session.session_key, product=product).exists()

    context = {
        'product': product,
        'related_products': related_products,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'store/product_detail.html', context)

def wishlist(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user)
    else:
        wishlist_items = Wishlist.objects.filter(session_key=session_key)

    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})

def cart(request):
    cart = _get_or_create_cart(request)
    cart_items = cart.items.all()
    subtotal = sum(item.total_price for item in cart_items)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': subtotal,  # Add tax/shipping calculations if needed
    }
    return render(request, 'store/cart.html', context)

def checkout(request):
    cart = _get_or_create_cart(request)
    cart_items = cart.items.all()
    if not cart_items:
        return redirect('store:cart')

    subtotal = sum(item.total_price for item in cart_items)
    
    if request.method == 'POST':
        # Create order
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address_line1 = request.POST.get('address_line1')
        address_line2 = request.POST.get('address_line2', '')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        payment_method = request.POST.get('payment_method', 'PhonePe')

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            state=state,
            postal_code=postal_code,
            total_amount=subtotal,
            payment_method=payment_method,
            status='Pending'
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.current_price,
                quantity=item.quantity
            )

        if payment_method == 'PhonePe':
            # Redirect to payments initiate view
            return redirect('payments:initiate', order_id=order.id)
        else:
            # Cash on Delivery: Mark success immediately
            order.status = 'Paid'  # Or COD pending status
            order.save()
            # Clear Cart
            cart.items.all().delete()
            return redirect('store:order_success', order_id=order.id)

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
    }
    return render(request, 'store/checkout.html', context)

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/order_success.html', {'order': order})

@login_required
def profile_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/profile.html', {'orders': orders})

# AJAX View: Add Item to Cart
@require_POST
def ajax_cart_add(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id)
        cart = _get_or_create_cart(request)
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        
        cart_count = sum(item.quantity for item in cart.items.all())
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart.',
            'cart_count': cart_count
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

# AJAX View: Update Item Quantity
@require_POST
def ajax_cart_update(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity'))
        
        if quantity <= 0:
            return JsonResponse({'success': False, 'message': 'Quantity must be at least 1'}, status=400)
            
        cart = _get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.quantity = quantity
        cart_item.save()
        
        subtotal = sum(item.total_price for item in cart.items.all())
        cart_count = sum(item.quantity for item in cart.items.all())
        
        return JsonResponse({
            'success': True,
            'item_total': float(cart_item.total_price),
            'cart_subtotal': float(subtotal),
            'cart_count': cart_count
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

# AJAX View: Remove Item from Cart
@require_POST
def ajax_cart_remove(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        cart = _get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        product_name = cart_item.product.name
        cart_item.delete()
        
        subtotal = sum(item.total_price for item in cart.items.all())
        cart_count = sum(item.quantity for item in cart.items.all())
        
        return JsonResponse({
            'success': True,
            'message': f'{product_name} removed from cart.',
            'cart_subtotal': float(subtotal),
            'cart_count': cart_count
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

# AJAX View: Toggle Wishlist Item
@require_POST
def ajax_wishlist_toggle(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        
        if request.user.is_authenticated:
            wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
            if wishlist_item:
                wishlist_item.delete()
                added = False
                msg = f'{product.name} removed from wishlist.'
            else:
                Wishlist.objects.create(user=request.user, product=product)
                added = True
                msg = f'{product.name} added to wishlist.'
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        else:
            wishlist_item = Wishlist.objects.filter(session_key=session_key, product=product).first()
            if wishlist_item:
                wishlist_item.delete()
                added = False
                msg = f'{product.name} removed from wishlist.'
            else:
                Wishlist.objects.create(session_key=session_key, product=product)
                added = True
                msg = f'{product.name} added to wishlist.'
            wishlist_count = Wishlist.objects.filter(session_key=session_key).count()
            
        return JsonResponse({
            'success': True,
            'added': added,
            'message': msg,
            'wishlist_count': wishlist_count
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

# Authentication Views
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('store:home')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('store:home')
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('store:home')

# AJAX View: Get Product Detail Modal Content
def ajax_product_modal(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    elif request.session.session_key:
        in_wishlist = Wishlist.objects.filter(session_key=request.session.session_key, product=product).exists()
        
    context = {
        'product': product,
        'in_wishlist': in_wishlist,
    }
    html = render_to_string('store/includes/product_modal_content.html', context, request=request)
    return JsonResponse({'html': html})

