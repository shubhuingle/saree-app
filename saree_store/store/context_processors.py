from .models import Cart, Wishlist

def cart_wishlist_count(request):
    cart_count = 0
    wishlist_count = 0
    
    # Get or create session if not present to ensure we have a session key
    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key
    user = request.user if request.user.is_authenticated else None

    # Cart Count
    try:
        if user:
            cart = Cart.objects.filter(user=user).first()
        else:
            cart = Cart.objects.filter(session_key=session_key).first()
            
        if cart:
            # sum of quantities
            cart_count = sum(item.quantity for item in cart.items.all())
    except Exception:
        pass

    # Wishlist Count
    try:
        if user:
            wishlist_count = Wishlist.objects.filter(user=user).count()
        else:
            wishlist_count = Wishlist.objects.filter(session_key=session_key).count()
    except Exception:
        pass

    return {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
    }
