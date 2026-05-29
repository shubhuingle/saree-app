/* ==========================================================================
   AJAX Wishlist Operations
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initWishlist();
});

function initWishlist() {
    document.addEventListener('click', (e) => {
        const toggleBtn = e.target.closest('.wishlist-toggle');
        if (toggleBtn) {
            e.preventDefault();
            const productId = toggleBtn.dataset.productId;
            toggleWishlist(productId, toggleBtn);
        }
    });
}

function toggleWishlist(productId, btnElement) {
    const csrftoken = getCSRFToken(); // from cart.js
    
    fetch('/ajax/wishlist/toggle/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            product_id: productId
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // Update badges
            const badge = document.getElementById('wishlistBadge');
            if (badge) badge.textContent = data.wishlist_count;
            
            // Toggle icon classes
            const icon = btnElement.querySelector('i');
            if (data.added) {
                icon.className = 'ph-fill ph-heart';
                icon.style.color = 'var(--accent-rose)';
                btnElement.classList.add('active');
            } else {
                icon.className = 'ph-bold ph-heart';
                icon.style.color = '';
                btnElement.classList.remove('active');
                
                // If we are on the wishlist page, remove the card from the DOM
                if (window.location.pathname === '/wishlist/') {
                    const card = btnElement.closest('.product-card-col');
                    if (card) {
                        card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                        card.style.opacity = '0';
                        card.style.transform = 'scale(0.9)';
                        setTimeout(() => {
                            card.remove();
                            // Check if empty
                            const grid = document.getElementById('wishlistGrid');
                            if (grid && grid.children.length === 0) {
                                window.location.reload();
                            }
                        }, 400);
                    }
                }
            }
            
            showToast(data.message);
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(err => {
        console.error('Wishlist error:', err);
        showToast('Could not update wishlist.', 'error');
    });
}
