from django.db import models
from django.contrib.auth.models import User

class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('gold', 'Premium Gold'),
        ('elite', 'Elite'),
        ('lifetime', 'Elite Lifetime'),
    ]
    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monthly Price")
    annual_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Annual Price (Leave blank for lifetime plans)")
    duration_text = models.CharField(max_length=50, help_text="e.g. 'Per Month', 'Once-off Payment'")
    description = models.TextField(blank=True, default="Elevate your fitness journey.")
    features = models.TextField(help_text="Checkmark separated by newlines")
    is_active = models.BooleanField(default=True)

    def get_features_list(self):
        return [f.strip() for f in self.features.split('\n') if f.strip()]

    def __str__(self):
        return f"{self.get_name_display()} - ₹{self.price}"

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name if self.plan else 'No Plan'}"
