import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitsync.settings')
django.setup()

from subscriptions.models import SubscriptionPlan

def sync_plans():
    # Clear existing to avoid confusion with case or old names
    SubscriptionPlan.objects.all().delete()
    
    plans_data = [
        {
            'name': 'basic',
            'price': 999,
            'annual_price': 6999,
            'duration_text': 'Per Month',
            'description': 'Essential features for your fitness journey.',
            'features': 'Gym Equipment\nBasic Protocols\nLocker Facility'
        },
        {
            'name': 'premium',
            'price': 1999,
            'annual_price': 12999,
            'duration_text': 'Per Month',
            'description': 'Advanced training for consistent results.',
            'features': 'AI Neural Training\nNutrition Coaching\nExpert Support'
        },
        {
            'name': 'elite',
            'price': 3999,
            'annual_price': 24999,
            'duration_text': 'Per Month',
            'description': 'Top-tier mentorship and total recovery.',
            'features': '1-on-1 Mentorship\nVIP Gym Access\nFull Recovery Spa'
        },
        {
            'name': 'lifetime',
            'price': 14999,
            'annual_price': None,
            'duration_text': 'One-time Payment',
            'description': 'The ultimate fitness investment.',
            'features': 'Unlimited Forever\nMaster Access\nVIP Perks'
        }
    ]

    for data in plans_data:
        plan = SubscriptionPlan.objects.create(
            name=data['name'],
            price=data['price'],
            annual_price=data['annual_price'],
            duration_text=data['duration_text'],
            description=data['description'],
            features=data['features'],
            is_active=True
        )
        print(f"Created plan: {plan.name}")

if __name__ == '__main__':
    sync_plans()
