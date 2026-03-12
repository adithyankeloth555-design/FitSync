from django import forms
from .models import (
    DietPlan, WorkoutProgram, BMIHistory, Attendance,
    UserProfile, Meal, Goal, NutritionLog, Message,
    CommunityPost, ExerciseVideo, HelpTicket, Product, Order,
)


class DietPlanForm(forms.ModelForm):
    class Meta:
        model = DietPlan
        fields = ['name', 'daily_calories', 'protein_g', 'carbs_g', 'fats_g', 'description']

class WorkoutProgramForm(forms.ModelForm):
    class Meta:
        model = WorkoutProgram
        fields = ['title', 'description', 'difficulty', 'frequency_per_week', 'asset_file']

class BMIHistoryForm(forms.ModelForm):
    class Meta:
        model = BMIHistory
        fields = ['weight_kg', 'height_cm', 'bmi_score']

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['workout_type', 'notes']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['fitness_goal', 'weight_kg', 'height_cm', 'phone_number', 'address', 'bio', 'profile_photo']

class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['day', 'name', 'calories', 'protein', 'carbs', 'fats', 'description', 'time']

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['title', 'category', 'start_value', 'current_value', 'target_value', 'unit', 'target_date', 'description']
        widgets = {
            'target_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class NutritionLogForm(forms.ModelForm):
    class Meta:
        model = NutritionLog
        fields = ['date', 'meal_type', 'food_item', 'calories', 'protein', 'carbs', 'fats']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver', 'subject', 'body']

class CommunityPostForm(forms.ModelForm):
    class Meta:
        model = CommunityPost
        fields = ['content', 'image']

class ExerciseVideoForm(forms.ModelForm):
    class Meta:
        model = ExerciseVideo
        fields = ['title', 'description', 'video_file', 'thumbnail']

class HelpTicketForm(forms.ModelForm):
    class Meta:
        model = HelpTicket
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'What can we help you with?'}),
            'message': forms.Textarea(attrs={'placeholder': 'Please provide details about your issue...', 'rows': 4}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'original_price', 'stock', 'badge', 'is_active', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
