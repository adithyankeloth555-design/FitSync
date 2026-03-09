import os
import django
import sys
from datetime import datetime
from django.utils import timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitsync.settings')
django.setup()

from django.contrib.auth.models import User
from fitsync_app.models import UserProfile, Payment
from subscriptions.models import UserSubscription, SubscriptionPlan

def restore_ashwin():
    print("=== Restoring Trainer Ashwin Keloth ===")
    
    # 1. Create Trainer User
    username = 'ashwin_keloth'
    email = 'ashwin@fitsync.com'
    password = 'trainer123'
    first_name = 'Ashwin'
    last_name = 'Keloth'
    
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
        print(f"[+] Created Trainer User: {username}")
    else:
        print(f"[*] Trainer User exists: {username}")
        
    # 2. Assign Trainer Role
    profile, p_created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'role': 'trainer',
            'specialty': 'CrossFit & Strength',
            'price': 5000.00, # Assuming a premium price
            'bio': 'Certified strength and conditioning specialist with 10 years of experience.'
        }
    )
    
    if p_created:
        print(f"[+] Created Profile for Trainer: {username}")
    else:
         # Ensure role is trainer if already existed but maybe changed
        if profile.role != 'trainer':
            profile.role = 'trainer'
            profile.save()
            print(f"[*] Updated Role to Trainer: {username}")
        else:
            print(f"[*] Profile exists for Trainer: {username}")

    # 3. Find User Adithyan
    try:
        adithyan = User.objects.get(username__iexact='adithyan')
        print(f"[FOUND] User: {adithyan.username}")
        
        # 4. Create Payment Record (Adithyan -> Ashwin)
        payment_amount = 5000.00
        payment, pay_created = Payment.objects.get_or_create(
            user=adithyan,
            trainer=user,
            defaults={
                'amount': payment_amount,
                'status': 'success',
                'transaction_id': f"ASHWIN-{adithyan.id}-PAYMENT",
                'payment_date': timezone.now()
            }
        )
        
        if pay_created:
             print(f"[+] Created Payment: {payment_amount} from {adithyan.username} to {username}")
        else:
             print(f"[*] Payment already exists: {payment_amount} from {adithyan.username} to {username}")
             
        # 5. Assign Ashwin as Adithyan's Trainer
        adithyan_profile = adithyan.userprofile
        adithyan_profile.assigned_trainer = user
        adithyan_profile.save()
        print(f"[+] Assigned {username} as trainer for {adithyan.username}")
        
        # 6. Ensure Adithyan has Elite Subscription (implied by high payment/personal trainer)
        elite_plan = SubscriptionPlan.objects.filter(name='elite').first()
        if elite_plan:
            sub, sub_created = UserSubscription.objects.get_or_create(user=adithyan)
            sub.plan = elite_plan
            sub.is_active = True
            sub.save()
            print(f"[+] Upgraded {adithyan.username} to Elite plan")

    except User.DoesNotExist:
        print("[!] User 'adithyan' not found. Cannot link payment.")

if __name__ == '__main__':
    restore_ashwin()
