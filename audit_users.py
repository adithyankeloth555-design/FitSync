import os
import django
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitsync.settings')
django.setup()

from django.contrib.auth.models import User
from fitsync_app.models import UserProfile

def audit_users():
    print("=== Current User Database Audit ===")
    print(f"{'ID':<5} {'Username':<20} {'Role':<10} {'Email':<30} {'Joined':<20}")
    print("-" * 85)
    
    users = User.objects.all().select_related('userprofile').order_by('date_joined')
    
    for user in users:
        role = 'N/A'
        if hasattr(user, 'userprofile'):
            role = user.userprofile.role
        elif user.is_superuser:
            role = 'superuser'
            
        print(f"{user.id:<5} {user.username:<20} {role:<10} {user.email:<30} {user.date_joined.strftime('%Y-%m-%d')}")

    print("-" * 85)
    print(f"Total Users in DB: {users.count()}")

if __name__ == '__main__':
    audit_users()
