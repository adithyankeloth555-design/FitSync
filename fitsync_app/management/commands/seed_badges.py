"""
Management command: seed_badges
Creates the default set of achievement badges in the database.
Run once after migration:
    python manage.py seed_badges
"""

from django.core.management.base import BaseCommand
from fitsync_app.models import Badge


BADGES = [
    {
        'code': 'first_bmi',
        'name': 'Vitality Pioneer',
        'description': 'Logged your first BMI reading.',
        'icon': 'fa-weight-scale',
        'color': '#10b981',
    },
    {
        'code': 'streak_7',
        'name': '7-Day Warrior',
        'description': 'Attended the gym 7 days in a row.',
        'icon': 'fa-fire',
        'color': '#f59e0b',
    },
    {
        'code': 'streak_30',
        'name': 'Iron Discipline',
        'description': 'Maintained a 30-day consecutive attendance streak.',
        'icon': 'fa-fire-flame-curved',
        'color': '#ef4444',
    },
    {
        'code': 'sessions_100',
        'name': 'Century Club',
        'description': 'Completed 100 workout sessions.',
        'icon': 'fa-trophy',
        'color': '#f9e295',
    },
    {
        'code': 'first_goal',
        'name': 'Goal Setter',
        'description': 'Created your first fitness goal.',
        'icon': 'fa-bullseye',
        'color': '#4F46E5',
    },
    {
        'code': 'goal_crusher',
        'name': 'Goal Crusher',
        'description': 'Completed 3 or more fitness goals.',
        'icon': 'fa-check-double',
        'color': '#8b5cf6',
    },
    {
        'code': 'hydration_hero',
        'name': 'Hydration Hero',
        'description': 'Logged water intake on 7 consecutive days.',
        'icon': 'fa-droplet',
        'color': '#06b6d4',
    },
    {
        'code': 'community_star',
        'name': 'Community Star',
        'description': 'Posted 5 times in the community forum.',
        'icon': 'fa-star',
        'color': '#f59e0b',
    },
]


class Command(BaseCommand):
    help = "Seed default achievement badges into the database"

    def handle(self, *args, **options):
        created = 0
        for data in BADGES:
            badge, is_new = Badge.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'icon': data['icon'],
                    'color': data['color'],
                }
            )
            if is_new:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"  [+] Created badge: {badge.name}"))
            else:
                self.stdout.write(f"  [-] Badge already exists: {badge.name}")

        self.stdout.write(self.style.SUCCESS(f"\nDone. Created {created} new badge(s)."))
