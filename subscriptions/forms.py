from django import forms
from .models import SubscriptionPlan

class SubscriptionPlanForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPlan
        fields = ['price', 'annual_price', 'duration_text', 'description', 'features', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'features': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Feature 1\nFeature 2\nFeature 3'}),
        }
