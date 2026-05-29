/* ==========================================================================
   AJAX Cart Drawer & Operations
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initCartDrawer();
});

// CSRF Token Retriever
function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === 'csrftoken=') {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}

function initCartDrawer() {
    const cartToggleBtn = document.getElementById('cartToggleBtn');
    const cartCloseBtn = document.getElementById('cartCloseBtn');
    const cartOverlay = document.getElementById('cartOverlay');
    const cartDrawer = document.getElementById('cartDrawer');

    if (!cartDrawer) return;

    // Toggle events
    cartToggleBtn.addEventListener('click', () => {
        openCartDrawer();
    });

    cartCloseBtn.addEventListener('click', () => {
        closeCartDrawer();
    });

    cartOverlay.addEventListener('click', () => {
        closeCartDrawer();
    });

    // Delegate cart events for quick add buttons
    document.addEventListener('click', (e) => {
        const quickAddBtn = e.target.closest('.quick-add-btn');
        if (quickAddBtn) {
            e.preventDefault();
            const productId = quickAddBtn.dataset.productId;
            addToCart(productId, 1);
        }
        
        // Remove item buttons inside drawer
        const removeBtn = e.target.closest('.remove-cart-item');
        if (removeBtn) {
            e.preventDefault();
            const itemId = removeBtn.dataset.itemId;
            removeCartItem(itemId);
        }
    });
}

function openCartDrawer() {
    const cartOverlay = document.getElementById('cartOverlay');
    const cartDrawer = document.getElementById('cartDrawer');
    
    cartOverlay.classList.add('active');
    cartDrawer.classList.add('active');
    
    // Load fresh cart content
    loadCartContent();
}

function closeCartDrawer() {
    const cartOverlay = document.getElementById('cartOverlay');
    const cartDrawer = document.getElementById('cartDrawer');
    
    cartOverlay.classList.remove('active');
    cartDrawer.classList.remove('active');
}

// Fetch Cart API and Render inside Side Drawer
function loadCartContent() {
    const drawerBody = document.getElementById('drawerCartBody');
    const subtotalText = document.getElementById('drawerSubtotal');
    
    fetch('/cart/')  // We request the cart page, but parse it or create a clean AJAX response
        .then(response => response.text())
        .then(html => {
            // To make integration extremely clean, we extract the cart-items-list container 
            // from the rendered page, or we fetch a custom JSON mapping if preferred.
            // Let's parse the HTML using DOMParser.
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const cartItemsContainer = doc.querySelector('.cart-items-container');
            const subtotalValue = doc.querySelector('#cartPageSubtotal')?.textContent || '₹0.00';
            
            if (cartItemsContainer && cartItemsContainer.children.length > 0) {
                drawerBody.innerHTML = cartItemsContainer.innerHTML;
                subtotalText.textContent = subtotalValue;
                
                // Attach event listeners to quantity inputs in drawer
                attachQuantityListeners(drawerBody);
            } else {
                drawerBody.innerHTML = `
                    <div class="empty-cart-message" style="text-align: center; padding: 40px 0;">
                        <i class="ph-bold ph-shopping-bag-open" style="font-size: 48px; color: var(--text-muted); margin-bottom: 15px; display:block;"></i>
                        <p style="color: var(--text-secondary);">Your shopping bag is empty.</p>
                        <a href="/products/" class="btn btn-gold btn-small" style="margin-top: 15px;">Shop Sarees</a>
                    </div>
                `;
                subtotalText.textContent = '₹0.00';
            }
        })
        .catch(err => {
            console.error('Error fetching cart:', err);
            drawerBody.innerHTML = '<p>Error loading shopping bag. Please try again.</p>';
        });
}

function attachQuantityListeners(container) {
    container.querySelectorAll('.qty-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const input = btn.parentElement.querySelector('.qty-input');
            const itemId = btn.dataset.itemId;
            let currentVal = parseInt(input.value);
            
            if (btn.classList.contains('plus')) {
                currentVal += 1;
            } else if (btn.classList.contains('minus') && currentVal > 1) {
                currentVal -= 1;
            }
            
            input.value = currentVal;
            updateCartQuantity(itemId, currentVal);
        });
    });
}

// Add Item AJAX API Call
function addToCart(productId, quantity) {
    const csrftoken = getCSRFToken();
    
    fetch('/ajax/cart/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // Update counts across the DOM
            document.getElementById('cartBadge').textContent = data.cart_count;
            document.getElementById('drawerCount').textContent = data.cart_count;
            
            showToast(data.message);
            openCartDrawer();
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(err => {
        console.error('Cart add error:', err);
        showToast('Failed to add saree. Try again.', 'error');
    });
}

// Update Item AJAX API Call
function updateCartQuantity(itemId, newQty) {
    const csrftoken = getCSRFToken();
    
    fetch('/ajax/cart/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            item_id: itemId,
            quantity: newQty
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // Update items total & subtotal on DOM
            document.getElementById('cartBadge').textContent = data.cart_count;
            document.getElementById('drawerCount').textContent = data.cart_count;
            
            // Reload cart elements to reflect totals
            loadCartContent();
            
            // If on cart page, reload page to sync
            if (window.location.pathname === '/cart/') {
                window.location.reload();
            }
        }
    })
    .catch(err => console.error('Cart update error:', err));
}

// Remove Item AJAX API Call
function removeCartItem(itemId) {
    const csrftoken = getCSRFToken();
    
    fetch('/ajax/cart/remove/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            item_id: itemId
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            document.getElementById('cartBadge').textContent = data.cart_count;
            document.getElementById('drawerCount').textContent = data.cart_count;
            
            showToast(data.message);
            loadCartContent();
            
            if (window.location.pathname === '/cart/') {
                window.location.reload();
            }
        }
    })
    .catch(err => console.error('Cart item remove error:', err));
}
