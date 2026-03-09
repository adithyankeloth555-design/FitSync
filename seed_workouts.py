import os
import django
import random
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitsync.settings')
django.setup()

from django.contrib.auth.models import User
from fitsync_app.models import WorkoutProgram, UserProfile

def seed_workouts():
    print("=== Seeding FitSync with Sample Workout Programs...")
    
    # Get a trainer
    trainer = User.objects.filter(userprofile__role='trainer').first()
    if not trainer:
        print("[ERROR] No trainer found. Please create a trainer first.")
        # Create a default trainer if none exists
        trainer, _ = User.objects.get_or_create(username='trainer_ashwin', email='ashwin@fitsync.com')
        trainer.set_password('trainer123')
        trainer.save()
        UserProfile.objects.get_or_create(user=trainer, defaults={'role': 'trainer'})
        print("[INFO] Created default trainer: trainer_ashwin")

    workout_templates = [
        {
            'title': 'Full Body Hypertrophy',
            'description': 'A comprehensive 3-day split focused on building lean muscle mass across all major groups. Includes compound movements like squats, deadlifts, and bench press.',
            'difficulty': 'intermediate',
            'frequency': 3
        },
        {
            'title': 'High-Intensity Interval Shred',
            'description': '20-minute intense cardio sessions designed to maximize calorie burn and improve cardiovascular endurance. No equipment needed.',
            'difficulty': 'beginner',
            'frequency': 4
        },
        {
            'title': 'Advanced Powerlifting Protocol',
            'description': 'Strict strength-focused program for experienced lifters targeting 1RM improvements in the big three lifts.',
            'difficulty': 'advanced',
            'frequency': 5
        },
        {
            'title': 'Mobility & Flexibility Flow',
            'description': 'Daily routines to improve range of motion, reduce injury risk, and enhance recovery. Perfect for rest days.',
            'difficulty': 'beginner',
            'frequency': 7
        },
        {
            'title': 'Athletic Performance Conditioning',
            'description': 'Explosive movements and agility drills to improve speed, power, and coordination for sports.',
            'difficulty': 'intermediate',
            'frequency': 4
        }
    ]

    count = 0
    for w in workout_templates:
        program, created = WorkoutProgram.objects.get_or_create(
            title=w['title'],
            defaults={
                'description': w['description'],
                'difficulty': w['difficulty'],
                'frequency_per_week': w['frequency'],
                'trainer': trainer
            }
        )
        if created:
            print(f"[OK] Created Workout: {w['title']}")
            count += 1
        else:
            print(f"[SKIP] Workout already exists: {w['title']}")

    print(f"\nSuccessfully added {count} new workout programs.")

if __name__ == "__main__":
    seed_workouts()
