import os
import django
import urllib.request
from django.core.files import File
from tempfile import NamedTemporaryFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zariegrace.settings')
django.setup()

from store.models import Category, Product, ProductImage, HomeBanner

def download_and_save_image(url, filename):
    try:
        print(f"Downloading {url}...")
        img_temp = NamedTemporaryFile(delete=True)
        # Add User-Agent header to avoid HTTP 403 Forbidden errors
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            img_temp.write(response.read())
        img_temp.flush()
        return File(img_temp, name=filename)
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return None

def seed():
    print("Starting database seeding...")
    
    # 1. Create Banners
    HomeBanner.objects.all().delete()
    banner_img = download_and_save_image(
        'https://images.unsplash.com/photo-1610030469983-98e550d6193c?q=80&w=1200', 
        'hero_banner.jpg'
    )
    if banner_img:
        HomeBanner.objects.create(
            title="Divine Handcrafted Sarees",
            subtitle="Explore our exclusive wedding and heritage edit designed for modern royalty",
            image=banner_img,
            cta_text="Shop Collection",
            cta_url="/products/",
            order=1,
            is_active=True
        )

    # 2. Create Categories
    Category.objects.all().delete()
    
    cat_data = [
        {
            'name': 'Heritage Silk',
            'desc': 'Exquisite pure Kanchipuram and Banarasi silk sarees crafted with gold zari threads.',
            'img_url': 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?q=80&w=600',
            'filename': 'cat_silk.jpg'
        },
        {
            'name': 'Luxe Georgette',
            'desc': 'Translucent flowing styles, embellished borders and lightweight silhouettes.',
            'img_url': 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?q=80&w=600',
            'filename': 'cat_georgette.jpg'
        },
        {
            'name': 'Ethereal Organza',
            'desc': 'Delicate, structured styles featuring classic prints and pastel palettes.',
            'img_url': 'https://images.unsplash.com/photo-1609357605129-26f69add5d6e?q=80&w=600',
            'filename': 'cat_organza.jpg'
        }
    ]
    
    categories = {}
    for c in cat_data:
        cat_file = download_and_save_image(c['img_url'], c['filename'])
        cat = Category.objects.create(
            name=c['name'],
            description=c['desc'],
            image=cat_file
        )
        categories[c['name']] = cat
        print(f"Created category: {c['name']}")

    # 3. Create Products
    Product.objects.all().delete()
    ProductImage.objects.all().delete()

    products_data = [
        {
            'category': 'Heritage Silk',
            'name': 'Gold Banarasi Zari Silk Saree',
            'price': 14999.00,
            'sale_price': 12499.00,
            'desc': 'Woven in the heart of Varanasi, this pure silk saree features detailed botanical motifs detailed in fine metallic gold threads. Ideal for weddings and legacy heirloom collections.',
            'stock': 8,
            'is_featured': True,
            'imgs': [
                'https://images.unsplash.com/photo-1610030469983-98e550d6193c?q=80&w=600',
                'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?q=80&w=600'
            ]
        },
        {
            'category': 'Heritage Silk',
            'name': 'Crimson Royal Kanchipuram Silk Saree',
            'price': 19999.00,
            'sale_price': 18999.00,
            'desc': 'Woven using three-ply premium mulberry silk from Kanchipuram. Rich border accents featuring classic temple architectures, paired with heavy pallu weaves.',
            'stock': 5,
            'is_featured': True,
            'imgs': [
                'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?q=80&w=600',
                'https://images.unsplash.com/photo-1610030469983-98e550d6193c?q=80&w=600'
            ]
        },
        {
            'category': 'Luxe Georgette',
            'name': 'Blush Sequence Border Saree',
            'price': 7899.00,
            'sale_price': 6899.00,
            'desc': 'Elegant sheer georgette in blush pink hue, detailed with dense hand-stitched silver sequence lining across the border. Features custom lightweight fit.',
            'stock': 12,
            'is_featured': True,
            'imgs': [
                'https://images.unsplash.com/photo-1609357605129-26f69add5d6e?q=80&w=600',
                'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?q=80&w=600'
            ]
        },
        {
            'category': 'Ethereal Organza',
            'name': 'Mint Green Floral Print Organza Saree',
            'price': 5999.00,
            'sale_price': 5499.00,
            'desc': 'Premium translucent organza, adorned with hand-painted pastel floral bouquets and detailed border trim. Very light weight, breathable, perfect for summer evening galas.',
            'stock': 15,
            'is_featured': True,
            'imgs': [
                'https://images.unsplash.com/photo-1609357605129-26f69add5d6e?q=80&w=600',
                'https://images.unsplash.com/photo-1610030469983-98e550d6193c?q=80&w=600'
            ]
        }
    ]

    for p in products_data:
        cat = categories[p['category']]
        product = Product.objects.create(
            category=cat,
            name=p['name'],
            price=p['price'],
            sale_price=p['sale_price'],
            description=p['desc'],
            stock=p['stock'],
            is_featured=p['is_featured']
        )
        print(f"Created product: {p['name']}")

        # Download and add multiple photos for listing
        for idx, img_url in enumerate(p['imgs']):
            p_file = download_and_save_image(img_url, f"p_{product.slug}_{idx}.jpg")
            if p_file:
                ProductImage.objects.create(
                    product=product,
                    image=p_file,
                    order=idx
                )
                print(f"Added image {idx} to {product.name}")

    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed()
