/* ==========================================================================
   Core Javascript: Theme, Smooth Scroll, Particles, Custom Cursor
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initCustomCursor();
    initSmoothScroll();
    initScrollReveal();
    initStarfield();
    initHeaderScroll();
    initProductQuickView();
});

/* ==========================================================================
   1. Theme Management (Light/Dark Switcher)
   ========================================================================== */
function initTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    
    if (!themeToggle || !themeIcon) return;

    // Check saved theme or default to dark
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme, themeIcon);

    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme, themeIcon);
        
        // Dispatch event for components that need to respond (like Canvas background)
        window.dispatchEvent(new CustomEvent('themechanged', { detail: newTheme }));
        showToast(`Switched to ${newTheme} mode`);
    });
}

function updateThemeIcon(theme, iconElement) {
    if (theme === 'dark') {
        iconElement.className = 'ph-bold ph-sun';
    } else {
        iconElement.className = 'ph-bold ph-moon';
    }
}

/* ==========================================================================
   2. Custom Lerp Cursor (AuraScenes / Antigravity Style)
   ========================================================================== */
function initCustomCursor() {
    const dot = document.getElementById('customCursorDot');
    const circle = document.getElementById('customCursorCircle');
    
    if (!dot || !circle) return;

    let mouseX = 0, mouseY = 0;
    let circleX = 0, circleY = 0;

    // Mouse coordinates updated immediately
    window.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        
        // Instantly position small dot
        dot.style.left = mouseX + 'px';
        dot.style.top = mouseY + 'px';
    });

    // Lerp algorithm for circle trailing effect
    function tick() {
        const lerpFactor = 0.15;
        circleX += (mouseX - circleX) * lerpFactor;
        circleY += (mouseY - circleY) * lerpFactor;
        
        circle.style.left = circleX + 'px';
        circle.style.top = circleY + 'px';
        
        requestAnimationFrame(tick);
    }
    tick();

    // Hover triggers
    const hoverElements = 'a, button, input, select, textarea, .product-card, .tab-btn, .qty-btn, .image-thumbnail';
    
    document.addEventListener('mouseover', (e) => {
        if (e.target.closest(hoverElements)) {
            document.body.classList.add('custom-cursor-hover');
        }
    });

    document.addEventListener('mouseout', (e) => {
        if (e.target.closest(hoverElements)) {
            document.body.classList.remove('custom-cursor-hover');
        }
    });
}

/* ==========================================================================
   3. Lenis Smooth Scroll Configuration
   ========================================================================== */
function initSmoothScroll() {
    // Only apply on desktop devices
    if (window.innerWidth < 768) return;

    try {
        const lenis = new Lenis({
            duration: 1.2,
            easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
            smoothWheel: true,
            smoothTouch: false
        });

        function raf(time) {
            lenis.raf(time);
            requestAnimationFrame(raf);
        }
        requestAnimationFrame(raf);
        
        // Link Lenis scroll state to GSAP ScrollTrigger
        lenis.on('scroll', ScrollTrigger.update);
        gsap.ticker.add((time)=>{
            lenis.raf(time * 1000);
        });
        gsap.ticker.lagSmoothing(0);
    } catch(e) {
        console.warn('Lenis could not initialize. Scrolling fallback to default.', e);
    }
}

/* ==========================================================================
   4. Intersection Observer for Scroll Reveals
   ========================================================================== */
function initScrollReveal() {
    const reveals = document.querySelectorAll('.reveal');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                // stop observing once active
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.15,
        rootMargin: '0px 0px -50px 0px'
    });

    reveals.forEach(el => observer.observe(el));
}

/* ==========================================================================
   5. Interactive Canvas Particle Background
   ========================================================================== */
function initStarfield() {
    // Create canvas dynamically to avoid template clutter
    const canvas = document.createElement('canvas');
    canvas.id = 'starfieldCanvas';
    document.body.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;
    
    let stars = [];
    const starCount = 65;
    
    let mouse = { x: null, y: null, radius: 150 };
    
    window.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });

    window.addEventListener('mouseout', () => {
        mouse.x = null;
        mouse.y = null;
    });

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    class Star {
        constructor() {
            this.reset();
        }
        
        reset() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.size = Math.random() * 1.5 + 0.5;
            this.speedX = (Math.random() - 0.5) * 0.15;
            this.speedY = (Math.random() - 0.5) * 0.15;
            this.baseAlpha = Math.random() * 0.5 + 0.1;
            this.alpha = this.baseAlpha;
            this.color = document.documentElement.getAttribute('data-theme') === 'dark' ? '245, 240, 232' : '141, 112, 62';
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;

            // Screen wrap boundaries
            if (this.x < 0 || this.x > width || this.y < 0 || this.y > height) {
                this.reset();
            }

            // Mouse proximity highlight
            if (mouse.x !== null && mouse.y !== null) {
                const dx = mouse.x - this.x;
                const dy = mouse.y - this.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < mouse.radius) {
                    const force = (mouse.radius - distance) / mouse.radius;
                    // Slightly nudge star away or increase brightness
                    this.alpha = Math.min(1.0, this.baseAlpha + force * 0.6);
                } else {
                    this.alpha = this.baseAlpha;
                }
            } else {
                this.alpha = this.baseAlpha;
            }
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${this.color}, ${this.alpha})`;
            ctx.fill();
        }
    }

    // Initialize stars array
    for (let i = 0; i < starCount; i++) {
        stars.push(new Star());
    }

    // React to theme swaps
    window.addEventListener('themechanged', (e) => {
        stars.forEach(star => {
            star.color = e.detail === 'dark' ? '245, 240, 232' : '141, 112, 62';
        });
    });

    // Animation Loop
    function animate() {
        ctx.clearRect(0, 0, width, height);
        stars.forEach(star => {
            star.update();
            star.draw();
        });
        requestAnimationFrame(animate);
    }
    animate();
}

/* ==========================================================================
   6. Global Toast Notifications Helper
   ========================================================================== */
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    
    let iconClass = 'ph-bold ph-check-circle';
    if (type === 'error') {
        iconClass = 'ph-bold ph-x-circle';
        toast.style.borderLeftColor = 'var(--accent-rose)';
    }
    
    toast.innerHTML = `<i class="${iconClass}"></i><span>${message}</span>`;
    container.appendChild(toast);

    // Fade out and remove
    setTimeout(() => {
        toast.style.animation = 'none';
        toast.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-10px)';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}

/* ==========================================================================
   7. Dynamic Header Sticky Scroll Management
   ========================================================================== */
function initHeaderScroll() {
    const root = document.documentElement;
    const header = document.querySelector('.glass-header');
    if (!header) return;

    const style = getComputedStyle(root);
    const announcementHeight = parseInt(style.getPropertyValue('--announcement-height')) || 40;
    const hasHero = document.querySelector('.hero-section') !== null;

    function handleScroll() {
        const scrollY = window.scrollY;
        const currentHeaderTop = Math.max(0, announcementHeight - scrollY);
        root.style.setProperty('--header-top', `${currentHeaderTop}px`);
        
        // If homepage has a hero section, keep header text white/transparent at top
        if (hasHero) {
            if (scrollY < 50) {
                header.classList.add('transparent-theme');
            } else {
                header.classList.remove('transparent-theme');
            }
        }
    }

    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
}

/* ==========================================================================
   8. Product Quick View Details Modal
   ========================================================================== */
function initProductQuickView() {
    const overlay = document.getElementById('productModalOverlay');
    const modal = document.getElementById('productQuickviewModal');
    const closeBtn = document.getElementById('productModalCloseBtn');
    const body = document.getElementById('productModalBody');

    if (!modal || !overlay) return;

    // Close button & overlay click
    closeBtn.addEventListener('click', closeModal);
    overlay.addEventListener('click', closeModal);

    // Escape key press to close
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
    });

    function openModal(slug) {
        overlay.classList.add('active');
        modal.classList.add('active');
        body.innerHTML = `
            <div class="loading-spinner">
                <i class="ph-bold ph-spinner spinner"></i>
            </div>
        `;

        fetch(`/ajax/product/modal/${slug}/`)
            .then(res => res.json())
            .then(data => {
                body.innerHTML = data.html;
                bindModalControls();
            })
            .catch(err => {
                console.error(err);
                body.innerHTML = '<p style="text-align:center; padding: 40px; color: var(--accent-rose);">Failed to load product details. Please try again.</p>';
            });
    }

    function closeModal() {
        overlay.classList.remove('active');
        modal.classList.remove('active');
    }

    function bindModalControls() {
        // Thumbnail switcher inside modal
        const mainImg = document.getElementById('modalHeroImage');
        const thumbs = body.querySelectorAll('.modal-thumb');
        thumbs.forEach(thumb => {
            thumb.addEventListener('click', () => {
                thumbs.forEach(t => t.classList.remove('active'));
                thumb.classList.add('active');
                mainImg.src = thumb.dataset.imgUrl;
            });
        });

        // Quantity selector inside modal
        const minusBtn = body.querySelector('.modal-minus');
        const plusBtn = body.querySelector('.modal-plus');
        const qtyInput = document.getElementById('modalQty');
        
        if (minusBtn && plusBtn && qtyInput) {
            minusBtn.addEventListener('click', () => {
                let val = parseInt(qtyInput.value);
                if (val > 1) qtyInput.value = val - 1;
            });

            plusBtn.addEventListener('click', () => {
                let val = parseInt(qtyInput.value);
                qtyInput.value = val + 1;
            });
        }

        // Add to Bag trigger inside modal
        const addToCartBtn = document.getElementById('modalAddToCart');
        if (addToCartBtn && qtyInput) {
            addToCartBtn.addEventListener('click', () => {
                const prodId = addToCartBtn.dataset.productId;
                const qty = parseInt(qtyInput.value);
                if (typeof addToCart === 'function') {
                    addToCart(prodId, qty);
                } else {
                    console.error('addToCart function not loaded');
                }
                closeModal();
            });
        }
    }

    // Intercept clicks on links globally using Event Delegation
    document.addEventListener('click', (e) => {
        const link = e.target.closest('.product-detail-link');
        if (link) {
            e.preventDefault();
            const slug = link.dataset.slug;
            openModal(slug);
        }
    });
}
