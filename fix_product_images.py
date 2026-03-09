import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitsync.settings')
django.setup()

from fitsync_app.models import Product

# Update Ab Roller
ab_roller = Product.objects.filter(name='Ab Roller').first()
if ab_roller:
    ab_roller.image = 'products/ab_roller.jpg'
    ab_roller.save()
    print("Updated Ab Roller image.")

# Update Workout Gloves
gloves = Product.objects.filter(name='Workout Gloves').first()
if gloves:
    gloves.image = 'products/workout_gloves.jpg'
    gloves.save()
    print("Updated Workout Gloves image.")

print("Product image correction complete.")
