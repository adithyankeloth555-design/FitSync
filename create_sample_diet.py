
import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitsync.settings')
django.setup()

from fitsync_app.models import DietPlan, Meal
from django.contrib.auth.models import User

# Get or create an admin user for attribution
user, _ = User.objects.get_or_create(username='admin')

# Create a sample diet plan
plan, created = DietPlan.objects.get_or_create(
    name="Metabolic Reset Protocol",
    defaults={
        'description': "A high-fidelity metabolic conditioning plan designed to optimize fat loss while preserving lean muscle mass.",
        'daily_calories': 1850,
        'protein_g': 180,
        'carbs_g': 150,
        'fats_g': 60,
        'trainer': user,
        'is_active': True
    }
)

if created:
    print(f"Created Diet Plan: {plan.name}")
else:
    print(f"Diet Plan {plan.name} already exists.")

# Add Meals for Monday
meals_data = [
    {
        'day': 'monday',
        'name': 'Breakfast',
        'calories': 450,
        'protein': 35,
        'carbs': 40,
        'fats': 15,
        'description': '4 Berries, Scrambled Eggs (3), and Whole Wheat Toast.',
        'time': '08:00'
    },
    {
        'day': 'monday',
        'name': 'Lunch',
        'calories': 600,
        'protein': 50,
        'carbs': 60,
        'fats': 18,
        'description': 'Grilled Chicken Salad with Quinoa and Avocado dressing.',
        'time': '13:00'
    },
    {
        'day': 'monday',
        'name': 'Snack',
        'calories': 200,
        'protein': 15,
        'carbs': 20,
        'fats': 8,
        'description': 'Greek Yogurt with Honey & Walnuts.',
        'time': '16:00'
    },
    {
        'day': 'monday',
        'name': 'Dinner',
        'calories': 600,
        'protein': 45,
        'carbs': 50,
        'fats': 20,
        'description': 'Baked Salmon with Brown Rice and Steamed Broccoli.',
        'time': '19:00'
    },
    # Tuesday
    {
        'day': 'tuesday',
        'name': 'Breakfast',
        'calories': 500,
        'protein': 30,
        'carbs': 55,
        'fats': 18,
        'description': 'Oatmeal with Almond Butter and Banana slices.',
        'time': '08:00'
    },
]

for m in meals_data:
    Meal.objects.create(diet_plan=plan, **m)
    print(f"Added meal: {m['name']} for {m['day']}")

print("Sample diet plan created successfully!")
