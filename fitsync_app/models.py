from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# 1. User Profile extending default User
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('trainer', 'Trainer'),
        ('admin', 'Administrator'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    fitness_goal = models.CharField(max_length=255, blank=True, null=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    
    # Extended Profile Fields
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    specialty = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=50.00) # Monthly price for trainers
    
    # Relationship
    assigned_trainer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='trainees')
    active_diet      = models.ForeignKey('DietPlan', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_users')
    active_workout   = models.ForeignKey('WorkoutProgram', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_users')
    
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def bmi(self):
        try:
            if self.weight_kg and self.height_cm and self.height_cm > 0:
                w = float(self.weight_kg)
                h = float(self.height_cm) / 100
                return round(w / (h * h), 1)
        except:
            pass
        return None

    @property
    def bmi_category(self):
        val = self.bmi
        if val:
            if val < 18.5: return "Underweight"
            if val < 25: return "Normal"
            if val < 30: return "Overweight"
            return "Obese"
        return "N/A"

    def __str__(self):
        return f"{self.user.username} ({self.role})"

# 2. Nutrition / Diet Plans
class DietPlan(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    daily_calories = models.IntegerField()
    protein_g = models.IntegerField()
    carbs_g = models.IntegerField()
    fats_g = models.IntegerField()
    trainer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_diets')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 3. Workout Programs
class WorkoutProgram(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    frequency_per_week = models.IntegerField()
    trainer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_workouts')
    asset_file = models.FileField(upload_to='workout_files/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# 4. BMI History Tracking
class BMIHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bmi_records')
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2)
    bmi_score = models.DecimalField(max_digits=4, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def get_category_display(self):
        if self.bmi_score < 18.5: return "Underweight"
        if self.bmi_score < 25: return "Normal Weight"
        if self.bmi_score < 30: return "Overweight"
        return "Obese"

# 5. Attendance Logs
class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_logs')
    workout_type = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    logged_at = models.DateTimeField(auto_now_add=True)

# 6. Meals within Diet Plans
class Meal(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    diet_plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE, related_name='meals')
    day = models.CharField(max_length=10, choices=DAY_CHOICES, default='monday')
    name = models.CharField(max_length=100) # e.g. Breakfast
    calories = models.IntegerField()
    protein = models.IntegerField()
    carbs = models.IntegerField()
    fats = models.IntegerField()
    description = models.TextField()
    time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.diet_plan.name}"

# 7. Payments and Subscriptions
class Payment(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    trainer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments_received')
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(auto_now_add=True)



# 9. System Notifications
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

# 10. Goals
class Goal(models.Model):
    CATEGORY_CHOICES = [
        ('weight', 'Weight Loss'),
        ('muscle', 'Muscle Gain'),
        ('endurance', 'Endurance/Cardio'),
        ('nutrition', 'Nutrition'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    
    # Progress Tracking
    start_value = models.FloatField(default=0.0)
    current_value = models.FloatField(default=0.0)
    target_value = models.FloatField(default=100.0)
    unit = models.CharField(max_length=20, default='kg') # kg, lbs, km, steps, %
    
    target_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_progress_percent(self):
        if self.is_completed:
            return 100
            
        # Calculate real percentage between start and target
        if self.target_value == self.start_value: 
            return 100 if self.current_value == self.target_value else 0
            
        total_required = abs(self.target_value - self.start_value)
        current_progress = abs(self.current_value - self.start_value)
        
        # If they moved in the wrong direction
        if (self.target_value > self.start_value and self.current_value < self.start_value) or \
           (self.target_value < self.start_value and self.current_value > self.start_value):
            return 0
            
        percent = (current_progress / total_required) * 100
        return min(100, max(0, percent))

    def __str__(self):
        return f"{self.user.username} - {self.title}"

# 11. Daily Nutrition Log
class NutritionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nutrition_logs')
    date = models.DateField(default=timezone.now)
    meal_type = models.CharField(max_length=50) # Breakfast, Lunch, Dinner, Snack
    food_item = models.CharField(max_length=255)
    calories = models.IntegerField()
    protein = models.IntegerField()
    carbs = models.IntegerField()
    fats = models.IntegerField()
    
    def __str__(self):
        return f"{self.user.username} - {self.food_item} ({self.date})"

class WaterLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='water_logs')
    date = models.DateField(default=timezone.now)
    amount_ml = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount_ml}ml on {self.date}"

# 12. Messages
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender} to {self.receiver}"

# 13. Trainer Feedback
class TrainerFeedback(models.Model):
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_feedback')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_feedback')
    feedback_text = models.TextField()
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback from {self.trainer.username} to {self.user.username}"

# 14. Community
class CommunityPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='community_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"

class CommunityComment(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# 15. Exercise Video Gallery
class ExerciseVideo(models.Model):
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_videos')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to='exercise_videos/')
    thumbnail = models.ImageField(upload_to='video_thumbnails/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# 16. Help Center Tickets
class HelpTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='help_tickets')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    admin_response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.subject}"

    class Meta:
        ordering = ['-created_at']

# 17. Email OTP for Registration
class EmailOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        # OTP valid for 10 minutes
        return (timezone.now() - self.created_at).total_seconds() > 600

    def __str__(self):
        return f"OTP for {self.email} - {self.otp}"

# 18. Smart Fitness Assessment
class FitnessAssessment(models.Model):
    GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('general_fitness', 'General Fitness'),
        ('endurance', 'Improve Endurance'),
        ('flexibility', 'Flexibility & Mobility'),
    ]
    ACTIVITY_CHOICES = [
        ('beginner', 'Beginner (0–1 workouts/week)'),
        ('intermediate', 'Intermediate (2–3 workouts/week)'),
        ('advanced', 'Advanced (4+ workouts/week)'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Prefer not to say'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='fitness_assessment')
    
    # Assessment inputs
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='other')
    height_cm = models.DecimalField(max_digits=5, decimal_places=1)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=1)
    fitness_goal = models.CharField(max_length=30, choices=GOAL_CHOICES)
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    health_issues = models.TextField(blank=True, null=True, help_text="Any medical conditions or injuries")
    target_weight_kg = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    
    # Computed outputs (stored as JSON-like text for simplicity)
    bmi_score = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    bmi_category = models.CharField(max_length=30, blank=True)
    
    completed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_bmi(self):
        h = float(self.height_cm) / 100
        w = float(self.weight_kg)
        bmi_val = w / (h * h)
        return float(f'{bmi_val:.1f}')

    def get_bmi_category(self):
        bmi = self.calculate_bmi()
        if bmi < 18.5: return "Underweight"
        elif bmi < 25: return "Normal Weight"
        elif bmi < 30: return "Overweight"
        else: return "Obese"

    def get_daily_calories(self):
        """Mifflin-St Jeor BMR estimate → TDEE"""
        w = float(self.weight_kg)
        h = float(self.height_cm)
        a = self.age
        if self.gender == 'male':
            bmr = (10 * w) + (6.25 * h) - (5 * a) + 5
        else:
            bmr = (10 * w) + (6.25 * h) - (5 * a) - 161

        multiplier = {'beginner': 1.375, 'intermediate': 1.55, 'advanced': 1.725}
        tdee = bmr * multiplier.get(self.activity_level, 1.375)

        if self.fitness_goal == 'weight_loss':
            return int(tdee - 400)
        elif self.fitness_goal == 'muscle_gain':
            return int(tdee + 300)
        return int(tdee)

    def __str__(self):
        return f"Assessment for {self.user.username}"


# 11. Live Trainer Sessions
class LiveSession(models.Model):
    trainer_name = models.CharField(max_length=100)
    session_title = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    meeting_link = models.URLField()
    workout_type = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.session_title} by {self.trainer_name}"


# ─── 19. FitSync Store ────────────────────────────────────────────────────────

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('protein', 'Protein & Supplements'),
        ('equipment', 'Equipment & Accessories'),
        ('apparel', 'Apparel & Gear'),
        ('recovery', 'Recovery & Wellness'),
    ]
    BADGE_CHOICES = [
        ('', 'None'),
        ('bestseller', 'Best Seller'),
        ('new', 'New Arrival'),
        ('sale', 'On Sale'),
        ('limited', 'Limited Stock'),
    ]
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='equipment')
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    stock = models.IntegerField(default=10)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    reviews_count = models.IntegerField(default=0)
    badge = models.CharField(max_length=20, choices=BADGE_CHOICES, blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    def total(self):
        return sum(item.total_price() for item in self.items.all())

    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    def total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    user           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='store_orders')
    total_amount   = models.DecimalField(max_digits=10, decimal_places=2)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    order_note     = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    # ── Structured Delivery Address ──────────────────────────────────────────
    full_name      = models.CharField(max_length=150, blank=True)
    phone          = models.CharField(max_length=20,  blank=True)
    house_address  = models.TextField(blank=True)               # House / Street / Area
    city           = models.CharField(max_length=100, blank=True)
    state          = models.CharField(max_length=100, blank=True)
    pincode        = models.CharField(max_length=10,  blank=True)
    country        = models.CharField(max_length=100, blank=True, default='India')

    def shipping_address(self):
        """Returns a single formatted address string for display."""
        parts = [self.house_address, self.city, self.state, self.pincode, self.country]
        return ', '.join(p for p in parts if p)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)  # Snapshot in case product deleted
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    def subtotal(self):
        return self.price * self.quantity


# ─── 20. Trainer Reviews (Member → Trainer) ─────────────────────────────────

class TrainerReview(models.Model):
    """A star-rating + comment left by a member for a trainer they've hired."""
    trainer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews_received'
    )
    member = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews_written'
    )
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1–5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        # One review per member per trainer
        unique_together = ('trainer', 'member')

    def __str__(self):
        return f"{self.member.username} → {self.trainer.username}: {self.rating}★"


# ─── 21. Badges / Achievements ───────────────────────────────────────────────

class Badge(models.Model):
    """Definition of an achievement badge."""
    BADGE_CHOICES = [
        ('first_bmi', 'First BMI Log'),
        ('streak_7', '7-Day Streak'),
        ('streak_30', '30-Day Streak'),
        ('sessions_100', '100 Sessions'),
        ('first_goal', 'First Goal Set'),
        ('goal_crusher', 'Goal Crusher'),
        ('hydration_hero', 'Hydration Hero'),
        ('community_star', 'Community Star'),
    ]
    code = models.CharField(max_length=30, choices=BADGE_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='fa-medal')   # FontAwesome class
    color = models.CharField(max_length=20, default='#4F46E5')    # Hex color

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    """Join table: which badges a user has earned."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earned_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='awarded_to')
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')
        ordering = ['-awarded_at']

    def __str__(self):
        return f"{self.user.username} – {self.badge.name}"
