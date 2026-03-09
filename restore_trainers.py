import os
import django
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitsync.settings')
django.setup()

from django.contrib.auth.models import User
from fitsync_app.models import UserProfile

def restore_trainers():
    print("=== Restoring Active Trainers ===")
    
    trainers = [
        ('trainer_mark', 'Mark', 'Johnson', 'mark@fitsync.com', 'trainer123'),
        ('trainer_sarah', 'Sarah', 'Williams', 'sarah@fitsync.com', 'trainer123'),
        ('trainer_david', 'David', 'Chen', 'david@fitsync.com', 'trainer123'),
        ('trainer_elena', 'Elena', 'Rodriguez', 'elena@fitsync.com', 'trainer123')
    ]
    
    for username, first_name, last_name, email, password in trainers:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            # Ensure profile exists
            UserProfile.objects.get_or_create(
                user=user, 
                defaults={
                    'role': 'trainer',
                    'specialty': 'General Fitness',
                    'price': 4000.00
                }
            )
            print(f"[+] Restored Trainer: {username}")
        else:
            print(f"[*] Trainer already exists: {username}")
            
    print(f"\nTotal Active Trainers: {UserProfile.objects.filter(role='trainer').count()}")

if __name__ == '__main__':
    restore_trainers()
