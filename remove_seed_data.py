import os
import django
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitsync.settings')
django.setup()

from django.contrib.auth.models import User
from fitsync_app.models import UserProfile, Payment, Attendance, Message, TrainerFeedback, NutritionLog, Goal, Notification

def clean_database():
    print("=== Cleaning up Example Data ===")
    
    # List of seed users from seed_db.py
    seed_usernames = [
        'trainer_mark', 'trainer_sarah', 
        'john_doe', 'jane_smith', 'mike_wilson', 
        'emma_brown', 'alex_davis', 'lisa_garcia'
    ]
    
    deleted_count = 0
    
    for username in seed_usernames:
        try:
            user = User.objects.get(username=username)
            print(f"[-] Deleting user: {username}")
            user.delete() # Cascades to Profile, Payments, Logs, etc.
            deleted_count += 1
        except User.DoesNotExist:
            print(f"[!] User not found (start clean): {username}")
            
    # Also clean up any payments/logs that might not have cascaded if users were manually deleted but data remained (unlikely with Django default, but good to be safe)
    # Actually, Django default is CASCADE, so deleting User deletes everything linked to it.
    
    print("-" * 30)
    print(f"Successfully removed {deleted_count} example users and their associated data.")
    print("Total Users Remaining:", User.objects.count())
    print("Total Payments Remaining:", Payment.objects.count())

if __name__ == '__main__':
    clean_database()
