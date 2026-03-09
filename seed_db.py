import os
import django
import random
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitsync.settings')
django.setup()

from django.contrib.auth.models import User
from fitsync_app.models import (
    UserProfile, Payment, Attendance, Message, 
    TrainerFeedback, NutritionLog, Goal, Notification
)
from subscriptions.models import UserSubscription

def seed_database():
    print("=== Seeding FitSync database with comprehensive data...")
    
    # 1. Create Admin
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@fitsync.com',
            'first_name': 'Admin',
            'last_name': 'Elite'
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        UserProfile.objects.get_or_create(user=admin_user, defaults={'role': 'admin'})
        print("[OK] Created Admin: admin / admin123")

    # 2. Create Trainers
    trainers = []
    trainer_data = [
        ('trainer_mark', 'Mark', 'Johnson', 'mark@fitsync.com', 'trainer123'),
        ('trainer_sarah', 'Sarah', 'Williams', 'sarah@fitsync.com', 'trainer123'),
    ]
    
    for username, first_name, last_name, email, password in trainer_data:
        trainer_user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name
            }
        )
        if created:
            trainer_user.set_password(password)
            trainer_user.save()
            UserProfile.objects.get_or_create(user=trainer_user, defaults={'role': 'trainer'})
            print(f"[OK] Created Trainer: {username} / {password}")
        trainers.append(trainer_user)

    # 3. Create Members with detailed profiles
    members = []
    member_data = [
        ('john_doe', 'John', 'Doe', 'john@example.com', 'user123', 75.5, 175.0, 'Build Muscle'),
        ('jane_smith', 'Jane', 'Smith', 'jane@example.com', 'user123', 62.0, 165.0, 'Weight Loss'),
        ('mike_wilson', 'Mike', 'Wilson', 'mike@example.com', 'user123', 82.0, 180.0, 'Strength Training'),
        ('emma_brown', 'Emma', 'Brown', 'emma@example.com', 'user123', 58.0, 160.0, 'Fitness & Toning'),
        ('alex_davis', 'Alex', 'Davis', 'alex@example.com', 'user123', 70.0, 172.0, 'Endurance'),
        ('lisa_garcia', 'Lisa', 'Garcia', 'lisa@example.com', 'user123', 65.0, 168.0, 'Overall Fitness'),
    ]
    
    for username, first_name, last_name, email, password, weight, height, goal in member_data:
        member_user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name
            }
        )
        if created:
            member_user.set_password(password)
            member_user.save()
            UserProfile.objects.get_or_create(
                user=member_user,
                defaults={
                    'role': 'member',
                    'fitness_goal': goal,
                    'weight_kg': weight,
                    'height_cm': height
                }
            )
            
            # Add subscription - first get or create a plan
            from subscriptions.models import SubscriptionPlan
            plan_name = random.choice(['basic', 'gold', 'elite'])
            plan, _ = SubscriptionPlan.objects.get_or_create(
                name=plan_name,
                defaults={
                    'price': {'basic': 1500.00, 'gold': 2500.00, 'elite': 5000.00}[plan_name],
                    'duration_text': 'Per Month' if plan_name != 'elite' else 'Lifetime',
                    'features': 'Access to gym\nPersonal trainer\nNutrition plan'
                }
            )
            UserSubscription.objects.get_or_create(
                user=member_user,
                defaults={
                    'plan': plan,
                    'is_active': True
                }
            )
            
            # Add payment
            Payment.objects.create(
                user=member_user,
                transaction_id=f"TXN{random.randint(10000, 99999)}",
                amount=random.choice([1500.00, 2500.00, 5000.00]),
                status='success'
            )
            
            print(f"[OK] Created Member: {username} / {password}")
        members.append(member_user)

    # 4. Create Attendance Records (Last 30 days)
    print("\n[ATTENDANCE] Creating attendance records...")
    for member in members:
        # Random attendance for last 30 days
        num_days = random.randint(15, 25)  # Attend 15-25 days out of 30
        for _ in range(num_days):
            days_ago = random.randint(0, 30)
            workout_types = ['Strength Training', 'Cardio', 'HIIT', 'Yoga', 'CrossFit', 'Boxing']
            Attendance.objects.create(
                user=member,
                workout_type=random.choice(workout_types),
                logged_at=datetime.now() - timedelta(days=days_ago)
            )
    print(f"[OK] Created {Attendance.objects.count()} attendance records")

    # 5. Create Messages between trainers and members
    print("\n[MESSAGES] Creating messages...")
    message_templates = [
        "Great workout today! Keep up the excellent form.",
        "Remember to focus on your nutrition this week.",
        "Your progress is amazing! Let's increase the intensity.",
        "Don't forget to stretch after your workouts.",
        "I noticed improvement in your technique. Well done!",
        "Let's schedule a form check session this week.",
        "Your dedication is inspiring. Keep pushing!",
        "Remember to stay hydrated during workouts.",
    ]
    
    for member in members:
        trainer = random.choice(trainers)
        # Create 3-5 messages per member
        for _ in range(random.randint(3, 5)):
            days_ago = random.randint(0, 7)
            
            # Trainer to member
            Message.objects.create(
                sender=trainer,
                receiver=member,
                body=random.choice(message_templates),
                sent_at=datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23)),
                is_read=random.choice([True, False])
            )
            
            # Member to trainer (response)
            if random.choice([True, False]):
                member_responses = [
                    "Thank you! I'll work on that.",
                    "Appreciate the feedback!",
                    "Will do, thanks coach!",
                    "Looking forward to it!",
                    "Thanks for the motivation!",
                ]
                Message.objects.create(
                    sender=member,
                    receiver=trainer,
                    body=random.choice(member_responses),
                    sent_at=datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23)),
                    is_read=random.choice([True, False])
                )
    print(f"[OK] Created {Message.objects.count()} messages")

    # 6. Create Trainer Feedback
    print("\n[FEEDBACK] Creating trainer feedback...")
    feedback_templates = [
        "Excellent progress this month! Your form has improved significantly, especially on squats and deadlifts. Keep maintaining proper posture and gradually increase weight. Focus on protein intake to support muscle recovery.",
        "Great dedication to your fitness journey! I've noticed consistent attendance and effort. Work on your cardio endurance - try adding 5 minutes to your running sessions each week. Your strength gains are impressive!",
        "Outstanding work ethic! Your technique on compound movements is solid. Next phase: let's focus on explosive power training. Remember to prioritize rest days for optimal recovery and muscle growth.",
        "Impressive transformation! Your commitment to both training and nutrition is paying off. Continue with the current program but increase intensity by 10%. Don't forget mobility work to prevent injuries.",
        "Fantastic progress on your fitness goals! Your endurance has improved remarkably. Let's add more resistance training to complement your cardio work. Keep tracking your macros - you're doing great!",
        "Solid performance this month! Your consistency is your biggest strength. Focus on mind-muscle connection during exercises. Consider adding yoga or stretching sessions for better flexibility and recovery.",
    ]
    
    for member in members:
        trainer = random.choice(trainers)
        # Create 1-3 feedback entries per member
        for _ in range(random.randint(1, 3)):
            days_ago = random.randint(1, 20)
            TrainerFeedback.objects.create(
                trainer=trainer,
                user=member,
                feedback_text=random.choice(feedback_templates),
                rating=random.randint(3, 5),  # 3-5 stars
                created_at=datetime.now() - timedelta(days=days_ago)
            )
    print(f"[OK] Created {TrainerFeedback.objects.count()} feedback entries")

    # 7. Create Nutrition Logs
    print("\n[NUTRITION] Creating nutrition logs...")
    for member in members:
        # Create logs for last 7 days
        for days_ago in range(7):
            date = datetime.now().date() - timedelta(days=days_ago)
            meals = [
                ('Breakfast', 'Oatmeal with Berries', 350, 12, 55, 8),
                ('Lunch', 'Grilled Chicken Salad', 450, 35, 25, 18),
                ('Dinner', 'Salmon with Vegetables', 520, 40, 30, 22),
                ('Snack', 'Protein Shake', 200, 25, 15, 5),
            ]
            for meal_type, food, cal, prot, carbs, fats in random.sample(meals, random.randint(2, 4)):
                NutritionLog.objects.create(
                    user=member,
                    date=date,
                    meal_type=meal_type,
                    food_item=food,
                    calories=cal,
                    protein=prot,
                    carbs=carbs,
                    fats=fats
                )
    print(f"[OK] Created {NutritionLog.objects.count()} nutrition logs")

    # 8. Create Goals
    print("\n[GOALS] Creating member goals...")
    goal_templates = [
        ('Lose 10kg', 'Achieve healthy weight through consistent training and nutrition'),
        ('Bench Press 100kg', 'Increase upper body strength progressively'),
        ('Run 5K in under 25 minutes', 'Improve cardiovascular endurance'),
        ('Attend gym 5 days/week', 'Build consistent workout routine'),
        ('Gain 5kg muscle mass', 'Focus on hypertrophy training and protein intake'),
        ('Master pull-ups', 'Achieve 10 consecutive pull-ups with proper form'),
    ]
    
    for member in members:
        # Create 2-3 goals per member
        for _ in range(random.randint(2, 3)):
            title, description = random.choice(goal_templates)
            Goal.objects.create(
                user=member,
                title=title,
                description=description,
                target_date=datetime.now().date() + timedelta(days=random.randint(30, 90)),
                is_completed=random.choice([True, False, False, False])  # 25% completed
            )
    print(f"[OK] Created {Goal.objects.count()} goals")

    # 9. Create Notifications
    print("\n[NOTIFICATIONS] Creating notifications...")
    notification_templates = [
        ('New Feedback Available', 'Your trainer has provided feedback on your recent performance.'),
        ('Workout Reminder', 'Don\'t forget your scheduled workout session today!'),
        ('Goal Milestone', 'You\'re 50% closer to achieving your fitness goal!'),
        ('New Message', 'You have a new message from your trainer.'),
        ('Subscription Renewal', 'Your subscription will renew in 7 days.'),
    ]
    
    for member in members:
        # Create 2-4 notifications per member
        for _ in range(random.randint(2, 4)):
            title, message = random.choice(notification_templates)
            days_ago = random.randint(0, 5)
            Notification.objects.create(
                user=member,
                title=title,
                message=message,
                is_read=random.choice([True, False]),
                created_at=datetime.now() - timedelta(days=days_ago)
            )
    print(f"[OK] Created {Notification.objects.count()} notifications")

    # Summary
    print("\n" + "="*60)
    print("*** DATABASE SEEDING COMPLETE! ***")
    print("="*60)
    print(f"\nSummary:")
    print(f"   Users: {User.objects.count()}")
    print(f"   Members: {User.objects.filter(userprofile__role='member').count()}")
    print(f"   Trainers: {User.objects.filter(userprofile__role='trainer').count()}")
    print(f"   Attendance Records: {Attendance.objects.count()}")
    print(f"   Messages: {Message.objects.count()}")
    print(f"   Feedback Entries: {TrainerFeedback.objects.count()}")
    print(f"   Nutrition Logs: {NutritionLog.objects.count()}")
    print(f"   Goals: {Goal.objects.count()}")
    print(f"   Notifications: {Notification.objects.count()}")
    
    print("\nLogin Credentials:")
    print("   Admin:    admin / admin123")
    print("   Trainer:  trainer_mark / trainer123")
    print("   Trainer:  trainer_sarah / trainer123")
    print("   Member:   john_doe / user123")
    print("   Member:   jane_smith / user123")
    print("   Member:   mike_wilson / user123")
    print("   (+ 3 more members with same password)")
    print("\n*** Your FitSync database is ready for testing! ***")

if __name__ == "__main__":
    seed_database()
