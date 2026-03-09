import os
import django
import sys
from django.db.models import Q

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitsync.settings')
django.setup()

from django.contrib.auth.models import User
from fitsync_app.models import UserProfile, Payment

def check_data():
    print("=== Checking for specific users and payments ===")
    
    # Check for Adithyan
    try:
        adithyan = User.objects.get(username__icontains='adithyan')
        print(f"[FOUND] User: {adithyan.username} (ID: {adithyan.id})")
    except User.DoesNotExist:
        print("[MISSING] User 'adithyan' not found.")
        adithyan = None
        
    # Check for Ashwin Keloth
    # Search by username or first/last name
    ashwin = User.objects.filter(
        Q(username__icontains='ashwin') | 
        Q(first_name__icontains='Ashwin') |
        Q(last_name__icontains='Keloth')
    ).first()
    
    if ashwin:
        print(f"[FOUND] Trainer: {ashwin.username} (ID: {ashwin.id}) - Role: {ashwin.userprofile.role}")
    else:
        print("[MISSING] Trainer 'Ashwin Keloth' not found.")
        
    # Check for payments
    if adithyan and ashwin:
        payments = Payment.objects.filter(user=adithyan, trainer=ashwin)
        if payments.exists():
            print(f"[FOUND] {payments.count()} payment(s) from {adithyan.username} to {ashwin.username}")
            for p in payments:
                print(f"  - Amount: {p.amount}, Date: {p.payment_date}, Status: {p.status}")
        else:
            print(f"[MISSING] No payments found from {adithyan.username} to {ashwin.username}")

if __name__ == '__main__':
    check_data()
