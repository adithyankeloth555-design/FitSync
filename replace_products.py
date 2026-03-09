import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitsync.settings')
django.setup()

from fitsync_app.models import Product

# 1. Remove all old products
Product.objects.all().delete()
print("Cleared existing products.")

# 2. Add new home workout equipment
products = [
    {
        'name': 'Resistance Band Set',
        'description': 'Premium 5-level resistance band set for full body workouts at home. Includes handles, door anchor, and ankle straps.',
        'price': 1499.00,
        'original_price': 2499.00,
        'category': 'equipment',
        'image': 'products/resistance_bands.png',
        'stock': 50,
        'badge': 'bestseller'
    },
    {
        'name': 'Yoga Mat',
        'description': 'Extra thick 6mm non-slip yoga mat with alignment lines. Perfect for yoga, pilates, and floor exercises.',
        'price': 999.00,
        'original_price': 1599.00,
        'category': 'equipment',
        'image': 'products/yoga_mat.png',
        'stock': 100,
        'badge': 'new'
    },
    {
        'name': 'Skipping Rope',
        'description': 'High-speed jumping rope with adjustable cable and ball bearings for smooth rotation.',
        'price': 499.00,
        'original_price': 799.00,
        'category': 'equipment',
        'image': 'products/skipping_rope.png',
        'stock': 200,
        'badge': ''
    },
    {
        'name': 'Push-up Bars',
        'description': 'Ergonomic S-shaped push-up stands with foam grip to reduce wrist strain and deepen push-ups.',
        'price': 799.00,
        'original_price': 1299.00,
        'category': 'equipment',
        'image': 'products/push_up_bars.png',
        'stock': 75,
        'badge': 'sale'
    },
    {
        'name': 'Adjustable Dumbbells',
        'description': 'Pair of 10kg adjustable dumbbells with high-quality steel plates and secure spin-lock collars.',
        'price': 4999.00,
        'original_price': 6999.00,
        'category': 'equipment',
        'image': 'products/dumbbells.png',
        'stock': 20,
        'badge': 'limited'
    },
    {
        'name': 'Foam Roller',
        'description': 'High-density trigger point foam roller for muscle recovery and deep tissue massage.',
        'price': 1299.00,
        'original_price': 1899.00,
        'category': 'equipment',
        'image': 'products/foam_roller.png',
        'stock': 40,
        'badge': ''
    },
    {
        'name': 'Ab Roller',
        'description': 'Ultra-wide ab wheel with knee pad for stable core training and abdominal carving.',
        'price': 899.00,
        'original_price': 1499.00,
        'category': 'equipment',
        'image': 'products/foam_roller.png', # Reusing due to quota
        'stock': 60,
        'badge': ''
    },
    {
        'name': 'Workout Gloves',
        'description': 'Lycra workout gloves with padded palms and wrist support for better grip and protection.',
        'price': 699.00,
        'original_price': 999.00,
        'category': 'apparel',
        'image': 'products/foam_roller.png', # Reusing due to quota
        'stock': 150,
        'badge': ''
    }
]

for p_data in products:
    Product.objects.create(**p_data)
    print(f"Added: {p_data['name']}")

print("Store successfully updated with home workout equipment.")
