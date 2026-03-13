# 🏋️ FitSync Elite — User Dashboard Complete Documentation

> **Purpose**: This document explains every section of the User Dashboard in detail — what it does, how it works internally (backend logic), what data is shown, and how the user interacts with it. Prepared for project demonstration and viva.

---

## 📑 Table of Contents

1. [User Login & Signup](#1-user-login--signup)
2. [User Dashboard Home Page](#2-user-dashboard-home-page)
3. [Performance Stats Cards](#3-performance-stats-cards)
4. [Elite Performance Coach Section](#4-elite-performance-coach-section)
5. [Operational Modules (Quick Actions)](#5-operational-modules-quick-actions)
6. [Progress & Analytics Page](#6-progress--analytics-page)
7. [Workout System](#7-workout-system)
8. [Diet Plan System](#8-diet-plan-system)
9. [Nutrition & Hydration Tracker](#9-nutrition--hydration-tracker)
10. [BMI Calculator & Vitality History](#10-bmi-calculator--vitality-history)
11. [Goals Tracker](#11-goals-tracker)
12. [Attendance System](#12-attendance-system)
13. [Membership & Subscription](#13-membership--subscription)
14. [Payment System (Razorpay)](#14-payment-system-razorpay)
15. [Messaging System](#15-messaging-system)
16. [Community Forum](#16-community-forum)
17. [AI Neural Hub (AI Features)](#17-ai-neural-hub-ai-features)
18. [Live Sessions Module](#18-live-sessions-module)
19. [Exercise Video Gallery](#19-exercise-video-gallery)
20. [Settings Page](#20-settings-page)
21. [Help & Support Center](#21-help--support-center)
22. [Sidebar Navigation](#22-sidebar-navigation)
23. [Mobile Responsive Design](#23-mobile-responsive-design)
24. [FitSync Store (User & Admin)](#24-fitsync-store-user--admin)

---

## 1. User Login & Signup

### Login Page

| Property | Details |
|----------|---------|
| **URL** | `/login/` |
| **Template** | `login.html` |
| **View Function** | `login_view()` in `views.py` (Line 17) |

#### How It Works:
1. User enters **username** and **password**.
2. Django's `authenticate()` function verifies the credentials against the database.
3. If authentication is successful, the system checks the user's **role** from `UserProfile`:
   - `role = 'admin'` → Redirects to Admin Dashboard (`/admin/`)
   - `role = 'trainer'` → Redirects to Trainer Dashboard (`/dashboard/trainer/`)
   - `role = 'member'` → Redirects to User Dashboard (`/dashboard/user/`)
4. If authentication fails → Shows error message: *"Invalid username or password."*

```python
def login_view(request):
    user = authenticate(request, username=u, password=p)
    if user is not None:
        login(request, user)
        role = user.userprofile.role
        if role == 'admin':
            return redirect('admin_dashboard')
        elif role == 'trainer':
            return redirect('trainer_dashboard')
        return redirect('user_dashboard')
```

### Signup Page

| Property | Details |
|----------|---------|
| **URL** | `/signup/` |
| **Template** | `signup.html` |
| **View Function** | `signup_view()` in `views.py` (Line 80) |

#### How It Works:
1. User fills in: **First Name, Last Name, Username, Email, Phone Number, Password, Confirm Password**
2. **Validation checks**:
   - Password must be 8–12 characters
   - Email must be a valid `@gmail.com` address (regex validation)
   - Passwords must match
   - Username must not already exist
   - Email must not already be registered
3. **Email OTP Verification**:
   - System generates a **6-digit OTP** using `random.choices()`
   - OTP is stored in the `EmailOTP` model in the database
   - Email is sent using Django's `send_mail()` function with subject "Verify Your FitSync Account"
   - User is redirected to `/verify-otp/` page
4. **OTP Verification Page** (`verify_otp_view`):
   - User enters the 6-digit code received on their email
   - System checks the OTP against the `EmailOTP` table
   - If correct and not expired → Creates the `User` and `UserProfile` with `role='member'`
   - Redirects to login page with success message

```python
# OTP Generation
otp = ''.join(random.choices(string.digits, k=6))
EmailOTP.objects.create(email=e, otp=otp)

# After OTP verification - User Creation
user = User.objects.create_user(username=..., email=..., password=...)
UserProfile.objects.create(user=user, role='member', phone_number=...)
```

### Forgot Password

| Property | Details |
|----------|---------|
| **URL** | `/forgot-password/` |
| **View Function** | `forgot_password_view()` in `views.py` (Line 186) |

- User provides **username** + **email** for identity verification
- If matched → allows setting a new password (8–12 characters)
- Uses `user.set_password()` to securely hash the new password

---

## 2. User Dashboard Home Page

| Property | Details |
|----------|---------|
| **URL** | `/dashboard/user/` |
| **Template** | `user_dashboard.html` (729 lines) |
| **View Function** | `user_dashboard_view()` in `views.py` (Line 421) |
| **URL Name** | `user_dashboard` |
| **Access** | Only `role='member'` users (protected by `@login_required`) |

#### How It Works:

1. **Role Routing** — The view first checks the user's role:
   - If the user is a `trainer` → redirects to `/dashboard/trainer/`
   - If the user is an `admin` → redirects to `/admin/`
   - This ensures no one accesses the wrong dashboard

2. **Data Fetching** — The backend fetches:
   ```python
   recent_feedback = TrainerFeedback.objects.filter(user=request.user).order_by('-created_at')[:5]
   assigned_trainer = user_profile.assigned_trainer
   sub = UserSubscription.objects.filter(user=request.user, is_active=True).first()
   is_basic = sub and sub.plan.name == 'basic'
   ```

3. **Profile Photo Upload** — Users can click on their profile photo in the sidebar to upload a new one:
   ```python
   if request.method == 'POST' and request.FILES.get('profile_photo'):
       form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
       if form.is_valid():
           form.save()
   ```

The dashboard is divided into several visual sections described below.

---

## 3. Performance Stats Cards

Three stat cards are displayed at the top of the dashboard in a 3-column grid:

### Card 1: Biometric Index (BMI)

| Element | Description |
|---------|-------------|
| **Label** | "Biometric Index" |
| **Value** | User's latest BMI score from `BMIHistory` model |
| **Status Pill** | Color-coded health category |
| **Action Button** | "Update Vitals" → links to BMI Calculator |

**How BMI Status Works:**
```
BMI < 18.5        → "Underweight" (Red alert pill)
18.5 ≤ BMI < 25   → "Optimal Range" (Green success pill)  
25 ≤ BMI < 30     → "Overweight" (Red alert pill)
BMI ≥ 30          → "Obese" (Red alert pill)
```

**Data Source:** `user.bmi_records.first` — Gets the most recent BMI record from `BMIHistory` model.

### Card 2: Training Intensity

| Element | Description |
|---------|-------------|
| **Label** | "Training Intensity" |
| **Value** | Total number of attendance logs → `user.attendance_logs.count` |
| **Status Pill** | "Active Streak" (always green with fire icon) |
| **Description** | "Sessions recorded in current cycle" |

### Card 3: Membership Status

| Element | Description |
|---------|-------------|
| **Label** | "Subscription Tier" |
| **Value** | "FitSync Elite Access" |
| **Status Pill** | "Unified Member" (Gold) |
| **Description** | "Full access to all AI & Training protocols" |

**Membership Logic:**
- The platform follows a **Single Mandatory Plan** strategy.
- Post-signup, a **₹199 / 3-Month** subscription is required to unlock the dashboard.
- Users without an active subscription are restricted from all core modules.

---

## 4. Elite Performance Coach Section

This section shows the user's **assigned personal trainer** (if they have one).

### If User Has an Assigned Trainer (Premium/Elite):

A premium-styled card shows:

| Element | Description |
|---------|-------------|
| **Trainer Photo** | 110×110px rounded photo with gold border |
| **Trainer Name** | Full name or username |
| **Specialty** | e.g., "Master Performance Specialist" |
| **Status** | "Online Now" green badge |
| **Assignment Date** | When the trainer was assigned |
| **Action Buttons** | "Instant Message" (gold) + "Profile" (outline) |

**Backend Logic:**
```python
assigned_trainer = user_profile.assigned_trainer
trainer_profile = UserProfile.objects.filter(user=assigned_trainer).first()
trainer_display_name = assigned_trainer.get_full_name() or assigned_trainer.username
```

### If User is on Basic Plan (Locked):

A locked promotional card with:
- 🔒 Lock icon in gold
- Title: "Unlock Elite Guidance"
- Message: "1-on-1 coaching and custom feedback loops require an active Elite Membership."
- "Complete Protocol" button → links to Membership payment gateway

### If No Trainer Assigned:

This section is hidden entirely.

---

## 5. Operational Modules (Quick Actions)

The dashboard organizes features into 4 grid sections with clickable cards:

### Section 1: Operational Modules (4 cards)

| Card | Icon | Links To | Description |
|------|------|----------|-------------|
| **Training** | `fa-dumbbell` | `/workout/` | Execution protocols and AI-driven routine generation |
| **Fueling** | `fa-leaf` | `/diet/` | Metabolic optimization and meal scheduling |
| **Neural Hub** | `fa-brain` | `/ai-hub/` | Access the complete suite of AI training and fueling tools |
| **Analytics** | `fa-chart-line` | `/progress/` | Quantitative progress tracking and performance charts |

### Section 2: Biometric Tracking (4 cards)

| Card | Icon | Links To | Description |
|------|------|----------|-------------|
| **Attendance** | `fa-calendar-check` | `/attendance/` | Temporal check-ins and consistency mapping |
| **Hydration** | `fa-droplet` | `/nutrition/` | Water intake and electrolyte balancing |
| **Objectives** | `fa-bullseye` | `/goals/` | Defining and monitoring mission-critical milestones |
| **Vitality** | `fa-heart-pulse` | `/bmi/history/` | Cardiovascular metrics and biometric history |

### Section 3: Network & Status (4 cards)

| Card | Icon | Links To | Description |
|------|------|----------|-------------|
| **Membership** | `fa-crown` | `/membership/` | Access level management and tier updates |
| **Coaches** | `fa-user-tie` | `/trainers/` | Interface with professional performance staff |
| **Messaging** | `fa-comments` | `/messages/` | Encrypted communication with trainers |
| **Syndicate** | `fa-users` | `/community/` | Peer performance groups and challenges |

### Section 4: System Configuration (2 cards)

| Card | Icon | Links To | Description |
|------|------|----------|-------------|
| **Settings** | `fa-gear` | `/settings/` | System preferences and credential management |
| **Support** | `fa-circle-question` | `/help/` | Technical documentation and help protocols |

**Card Hover Effect:**
- Cards lift up 10px (`translateY(-10px)`)
- Gold border appears
- Background gradient changes
- Icon scales up and rotates slightly

---

## 6. Progress & Analytics Page

| Property | Details |
|----------|---------|
| **URL** | `/progress/` |
| **Template** | `progress.html` |
| **View Function** | `progress_view()` in `views.py` (Line 516) |
| **URL Name** | `progress` |

#### How It Works:

This page shows **comprehensive fitness analytics** with real data from the database.

**Stats Displayed:**

| Metric | How It's Calculated |
|--------|---------------------|
| **Weekly Attendance** | `Attendance.objects.filter(user=request.user, logged_at__gte=seven_days_ago).count()` |
| **Total Sessions** | `Attendance.objects.filter(user=request.user).count()` |
| **Calories Burned** | `total_attendance × 400` (estimated 400 cal/session) |
| **Steps** | `5000 + (total_attendance × 1200)` (derived from activity) |
| **Total Duration** | `total_attendance × 60` minutes (60 min/session) |
| **Weight Change** | `last_bmi_record.weight - first_bmi_record.weight` |

**Weekly Chart (Bar Chart):**
```python
for i in range(6, -1, -1):
    target_date = (now - timedelta(days=i)).date()
    count = Attendance.objects.filter(
        user=request.user, 
        logged_at__range=(day_start, day_end)
    ).count()
```
- Shows attendance count for each of the last 7 days
- Bar heights are proportionally scaled (0–200px)
- Each bar shows the day abbreviation (Mon, Tue, etc.)

**Weight History Chart:**
- Shows last 7 BMI records in chronological order
- Displays date labels and weight values

---

## 7. Workout System

| Property | Details |
|----------|---------|
| **URL** | `/workout/` |
| **Template** | `workout_list.html` |
| **View Function** | `workout_list_view()` in `views.py` (Line 1128) |
| **URL Name** | `workout_list` |

#### How It Works:

1. **Listing**: Fetches all `WorkoutProgram` objects from the database
2. **Check-in Status**: Checks if user has already marked attendance today:
   ```python
   already_checked_in = Attendance.objects.filter(
       user=request.user, logged_at__date=today
   ).exists()
   ```
3. **Workout Session** (`/workout/session/<pk>/`): Detailed view of a specific workout with exercises, sets, reps, and rest times
4. **Mark Attendance API** (`/api/attendance/mark/`): AJAX endpoint that creates an attendance record when user completes a workout:
   ```python
   Attendance.objects.create(
       user=request.user,
       workout_type=workout_type,
       notes=notes
   )
   ```

---

## 8. Diet Plan System

| Property | Details |
|----------|---------|
| **URL** | `/diet/` |
| **Template** | `diet_list.html` |
| **View Function** | `diet_list_view()` in `views.py` (Line 1006) |
| **URL Name** | `diet_list` |

#### How It Works:

1. **List View**: Shows all diet plans created by trainers
2. **Detail View** (`/diet/<pk>/`): Shows meals organized by **day of the week** (Monday–Sunday)
3. **Meals are grouped by day** with nutritional calculations:
   ```python
   days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
   meals_by_day = {day: meals.filter(day=day) for day in days}
   ```
4. **Daily Totals**: Calculates calories, protein, carbs, and fats per day:
   ```python
   monday_totals = {
       'calories': sum(m.calories for m in monday_meals),
       'protein': sum(m.protein for m in monday_meals),
       'carbs': sum(m.carbs for m in monday_meals),
       'fats': sum(m.fats for m in monday_meals),
   }
   ```
5. **User's role**: Only trainers/admins can add, edit, or delete diet plans. Members can only view them.

---

## 9. Nutrition & Hydration Tracker

| Property | Details |
|----------|---------|
| **URL** | `/nutrition/` |
| **Template** | `nutrition.html` |
| **View Function** | `nutrition_view()` in `views.py` (Line 773) |
| **URL Name** | `nutrition` |

#### How It Works:

1. **Meal Logging**: Users can log individual meals using `NutritionLogForm`:
   - Fields: Meal type, Food item, Calories, Protein, Carbs, Fats
   - Logs are saved to `NutritionLog` model tied to the current user and today's date

2. **Daily Totals Calculation**:
   ```python
   daily_logs = NutritionLog.objects.filter(user=request.user, date=today)
   totals = {
       'calories': sum(l.calories for l in daily_logs),
       'protein': sum(l.protein for l in daily_logs),
       'carbs': sum(l.carbs for l in daily_logs),
       'fats': sum(l.fats for l in daily_logs),
       'water': water_log.amount_ml,
   }
   ```

3. **Goals vs Progress**:
   ```python
   goals = {
       'calories': 2000,     # Daily calorie target
       'protein': 150,       # Daily protein target (grams)
       'carbs': 250,         # Daily carbs target (grams)
       'water': 2000,        # Daily water target (ml) = 8 glasses × 250ml
   }
   ```

4. **Remaining Nutrients**: Shows how much more the user needs to eat today
5. **Progress Percentage**: Percentage bars for calories and water intake

### Water Tracking (AJAX API):

| Property | Details |
|----------|---------|
| **URL** | `/api/nutrition/water/add/` |
| **View Function** | `add_water()` in `views.py` (Line 829) |

- User clicks a button to add water (e.g., +250ml per glass)
- AJAX POST request sends the amount
- Backend updates `WaterLog` model for today:
  ```python
  water_log, created = WaterLog.objects.get_or_create(user=request.user, date=today)
  water_log.amount_ml += amount
  water_log.save()
  ```
- Returns JSON response with new total (page updates without reload)

---

## 10. BMI Calculator & Vitality History

### BMI Calculator

| Property | Details |
|----------|---------|
| **URL** | `/bmi/calculator/` |
| **Template** | `bmi_calculator.html` |
| **View Function** | `bmi_calculator_view()` in `views.py` (Line 1171) |
| **URL Name** | `bmi_calculator` |

#### How It Works:

1. User enters **weight (kg)** and **height (cm)** on the frontend
2. **JavaScript calculates BMI** on the client side: `BMI = weight / (height_in_meters²)`
3. On form submit, the BMI value + weight + height are sent to the backend via POST
4. Backend creates a `BMIHistory` record:
   ```python
   BMIHistory.objects.create(
       user=request.user,
       weight_kg=w,
       height_cm=h,
       bmi_score=b
   )
   ```
5. Redirects to BMI History page

### BMI History (Vitality)

| Property | Details |
|----------|---------|
| **URL** | `/bmi/history/` |
| **Template** | `bmi_history.html` |
| **View Function** | `bmi_history_view()` in `views.py` (Line 1188) |
| **URL Name** | `bmi_history` |

- Shows all past BMI records for the logged-in user
- Displays: Date, Weight, Height, BMI Score
- Data is fetched: `BMIHistory.objects.filter(user=request.user)`

---

## 11. Goals Tracker

| Property | Details |
|----------|---------|
| **URL** | `/goals/` |
| **Template** | `goals.html` |
| **View Function** | `goals_view()` in `views.py` (Line 846) |
| **URL Name** | `goals` |

#### How It Works:

1. **Adding Goals**: User fills `GoalForm` (title, description, target date)
   ```python
   goal = form.save(commit=False)
   goal.user = request.user
   goal.save()
   ```

2. **Toggle Complete**: Each goal has a checkbox to mark complete/incomplete:
   ```python
   if 'toggle_complete' in request.POST:
       goal = get_object_or_404(Goal, id=goal_id, user=request.user)
       goal.is_completed = not goal.is_completed
       goal.save()
   ```

3. **Sorting**: Goals are ordered: incomplete first, then by newest:
   ```python
   goals = Goal.objects.filter(user=request.user).order_by('is_completed', '-created_at')
   ```

---

## 12. Attendance System

| Property | Details |
|----------|---------|
| **URL** | `/attendance/` |
| **Template** | `attendance.html` |
| **View Function** | `attendance_tracker_view()` in `views.py` (Line 620) |
| **URL Name** | `attendance` |

#### How It Works:

This is a rich, interactive attendance tracker with multiple views.

1. **Calendar Grid**: Generated using Python's `calendar.monthcalendar()`:
   ```python
   cal = calendar.monthcalendar(year, month)
   for week in cal:
       for day in week:
           calendar_days.append({
               'day': day,
               'is_present': day in present_days_in_month,
               'is_today': (day == local_now.day),
               'is_past': day > 0 and day < local_now.day
           })
   ```
   - Green highlight = Present day
   - Special highlight = Today's date
   - Gray = Past days without check-in

2. **14-Day Status Strip**: Shows last 14 days with present/absent markers:
   ```python
   for i in range(13, -1, -1):
       check_date = (local_now - timedelta(days=i)).date()
       is_present = check_date in all_present_dates
   ```

3. **Attendance Rate**: Percentage calculation:
   ```python
   attendance_rate = round((len(present_days_in_month) / local_now.day) * 100)
   ```

4. **Check-in Count**: Shows how many times user checked in today

5. **Mark Attendance**: Button to mark today's attendance (POST to `/attendance/mark/` or AJAX to `/api/attendance/mark/`)

---

## 13. Membership & Subscription

| Property | Details |
|----------|---------|
| **URL** | `/membership/` |
| **Template** | `membership.html` |
| **View Function** | `membership_view()` in `views.py` (Line 695) |
| **URL Name** | `membership` |

#### How It Works:

1. **Fetches subscription**: `UserSubscription.objects.get(user=request.user)`
2. **Fetches payment history**: `Payment.objects.filter(user=request.user).order_by('-payment_date')`
3. **Displays current plan info**:

| Display Field | How It's Calculated |
|---------------|---------------------|
| **Plan Name** | "FitSync Elite Access" |
| **Price** | "₹199.00" |
| **Billing Cycle** | "Quarterly (90 Days)" |
| **Valid Until** | From `subscription.expiry_date` |
| **Days Remaining** | `(expiry_date - now).days` |

**Pre-Payment Gating:**
- New users are redirected here immediately after OTP verification.
- access to `/dashboard/user/` and all fitness/AI modules is blocked using the `subscription_required` decorator/logic.
- Includes a secure **Razorpay Integration** for instant activation.

4. **Upgrade Options**: Shows all active plans from `SubscriptionPlan` model for the user to select

---

## 14. Payment System (Razorpay)

| Property | Details |
|----------|---------|
| **URLs** | `/payment/` (subscription) and `/payment/trainer/<id>/` (hire trainer) |
| **View Functions** | `payment_view()` (Line 1283) and `trainer_payment_view()` |

#### How Subscription Payment Works:

1. User selects a plan from the membership page
2. Redirected to payment page with `?plan=<plan_name>&billing=<monthly/annual>`
3. **Razorpay Checkout** loads with the plan price
4. After payment:
   ```python
   sub, created = UserSubscription.objects.get_or_create(user=request.user)
   sub.plan = selected_plan
   sub.is_active = True
   
   # Calculate Expiry Date
   if billing_cycle == 'annual':
       sub.expiry_date = timezone.now() + timedelta(days=365)
   elif selected_plan.name == 'lifetime':
       sub.expiry_date = timezone.now() + timedelta(days=36500)  # ~100 years
   else:
       sub.expiry_date = timezone.now() + timedelta(days=30)  # Monthly
   ```
5. Creates a `Payment` record with transaction ID, amount, and status

#### How Trainer Hiring Payment Works:

1. User selects a trainer from the Trainer List
2. Redirected to `/payment/trainer/<trainer_id>/`
3. Shows trainer info + pricing summary
4. Uses Razorpay for payment
5. After payment → assigns trainer to user: `user_profile.assigned_trainer = trainer`

---

## 15. Messaging System

| Property | Details |
|----------|---------|
| **URL** | `/messages/` |
| **Template** | `messages.html` |
| **View Function** | `messages_view()` in `views.py` (Line 869) |
| **URL Name** | `messages` |

#### How It Works:

1. **Contact List Building**:
   - **Members see**: All trainers and admins
   - **Trainers see**: Their assigned trainees
   - **Plus**: Anyone they've previously chatted with (for continuity)
   ```python
   # Members see trainers and admins
   contacts = User.objects.filter(
       userprofile__role__in=['trainer', 'admin']
   ).exclude(id=request.user.id)
   ```

2. **Active Conversation**: Selected via `?user_id=<id>` query parameter or defaults to first contact

3. **Sending Messages** (POST):
   ```python
   Message.objects.create(
       sender=request.user,
       receiver=receiver,
       body=content
   )
   ```

4. **Conversation Fetching**: Gets all messages between two users in chronological order:
   ```python
   messages_list = Message.objects.filter(
       Q(sender=request.user, receiver=active_user) | 
       Q(sender=active_user, receiver=request.user)
   ).order_by('sent_at')
   ```

---

## 16. Community Forum

| Property | Details |
|----------|---------|
| **URL** | `/community/` |
| **Template** | `community.html` |
| **View Function** | `community_view()` in `views.py` (Line 990) |
| **URL Name** | `community` |

#### How It Works:

1. **Creating Posts**: Users can share text and images:
   ```python
   form = CommunityPostForm(request.POST, request.FILES)
   if form.is_valid():
       post = form.save(commit=False)
       post.author = request.user
       post.save()
   ```

2. **Viewing Posts**: All posts displayed in reverse chronological order:
   ```python
   posts = CommunityPost.objects.all().order_by('-created_at')
   ```

3. **Features**: Post content, author info, timestamps, image attachments

---

## 17. AI Neural Hub (AI Features)

### AI Hub (Central Page)

| Property | Details |
|----------|---------|
| **URL** | `/ai-hub/` |
| **Template** | `ai_hub.html` |
| **View Function** | `ai_hub_view()` in `views.py` (Line 1389) |
| **URL Name** | `ai_hub` |

The AI Hub is the gateway to all AI features. It checks subscription status:
```python
sub = UserSubscription.objects.filter(user=request.user, is_active=True).first()
is_premium = sub and sub.plan.name != 'basic'
```

### AI Tools Available:

#### A. AI Chatbot (Nova AI)

| Property | Details |
|----------|---------|
| **URL** | `/chatbot/` |
| **API Endpoint** | `/api/chatbot/` (POST) |
| **View Function** | `chatbot_view()` + `chatbot_api_view()` |
| **Access** | Premium/Elite only (Basic users redirected to membership page) |

**How It Works (Dual-Mode):**

**Mode 1 — Gemini AI (Online):**
- If `GEMINI_API_KEY` is configured in settings:
  ```python
  genai.configure(api_key=api_key)
  model = genai.GenerativeModel('gemini-pro')
  response = model.generate_content(prompt)
  ```
- System prompt makes it act as "AI Coach" — a fitness-focused AI persona
- Uses Google's Gemini Pro model for natural language responses

**Mode 2 — Local Knowledge Base (Offline/Fallback):**
- If no API key or API call fails → uses a built-in keyword dictionary
- Contains 30+ entries covering:
  - **Nutrition**: protein, carbs, fat, creatine, calories, water, keto
  - **Exercises**: squat, deadlift, bench, pushup, pullup, plank, lunge, burpee
  - **Training Concepts**: hypertrophy, strength, cardio, HIIT, rest, sleep, yoga, stretching
  - **General**: weight loss, muscle gain, motivation, discipline
- Matching logic: Checks if any keyword exists in the user's message
  ```python
  for key, val in knowledge_base.items():
      if key in user_msg_lower:
          return JsonResponse({"reply": f"**AI COACH DATABASE:** {val}"})
  ```

#### B. AI Workout Generator

| Property | Details |
|----------|---------|
| **URL** | `/ai-workout/` |
| **View Function** | `ai_workout_view()` in `views.py` (Line 1526) |
| **Access** | Premium/Elite only |

- Generates personalized workout routines using AI
- Basic members see: *"Neural Workout Generation is reserved for Premium and Elite members."*

#### C. AI Diet Generator

| Property | Details |
|----------|---------|
| **URL** | `/ai-diet/` |
| **View Function** | `ai_diet_view()` in `views.py` (Line 1536) |
| **Access** | Premium/Elite only |

- Creates AI-powered meal plans based on user preferences
- Basic members see: *"AI Metabolic Fueling Protocols are reserved for Premium and Elite members."*

#### D. Computer Vision & Advanced AI

| Feature | Description |
|---------|-------------|
| **Exercise Detection** | Real-time form correction and rep counting using MediaPipe AI camera feed. |
| **Meal Scanner** | Photo-based calorie estimation and automated macro logging. |
| **Fitness Score** | Algorithm-derived performance rating (0-100) based on biological vectors. |
| **Habit Streaks** | Predictive engagement tracking with gamified badge unlocks. |

---

## 18. Live Sessions Module

| Property | Details |
|----------|---------|
| **URL** | `/live-session/` |
| **Template** | `live_session.html` |
| **View Function** | `live_session_view()` in `views.py` (Line 2555) |
| **URL Name** | `live_session` |

#### How It Works:

1. **Scheduling (Trainer Flow)**: Trainers create sessions with a title, date, time, and a secure meeting link (Google Meet/Zoom).
2. **Access (Member Flow)**: Members view upcoming sessions in a chronological list.
3. **One-Click Join**: Clicking "Join" redirects directly to the virtual room:
   ```python
   # live_session_room_view (Line 2603)
   session = get_object_or_404(LiveSession, id=session_id)
   return redirect(session.meeting_link)
   ```
4. **Visibility**: Only sessions for today and the future are displayed to keep the dashboard clean.

---

## 18. Exercise Video Gallery

| Property | Details |
|----------|---------|
| **URL** | `/videos/` |
| **Template** | `video_gallery.html` |
| **View Function** | `video_gallery_view()` in `views.py` (Line 1660) |
| **URL Name** | `video_gallery` |

#### How It Works:

1. **Shows all exercise videos** uploaded by trainers:
   ```python
   videos = ExerciseVideo.objects.all().order_by('-created_at')
   ```
2. **User (member) can only watch** — the upload button is hidden for non-trainers
3. Videos include: Title, description, exercise category, upload date, trainer name

---

## 19. Settings Page

| Property | Details |
|----------|---------|
| **URL** | `/settings/` |
| **Template** | `settings.html` |
| **View Function** | `settings_view()` in `views.py` (Line 933) |
| **URL Name** | `settings` |

#### How It Works:

Users can update their comprehensive profile information:

| Field | Description | Model Mapping |
|-------|-------------|---------------|
| **Full Name** | Split into first and last name targets. | `user.first_name`, `user.last_name` |
| **Email** | Validated @gmail link. | `user.email` |
| **Phone** | Mobile contact logic. | `profile.phone_number` |
| **Specialization** | For trainers only (e.g. Strength Coach). | `profile.specialty` |
| **Bio/Address** | Regional and descriptive data. | `profile.bio`, `profile.address` |
| **Biometrics** | Base weight and height for BMI calcs. | `profile.weight_kg`, `profile.height_cm` |
| **Photo** | Profile avatar (Media storage). | `profile.profile_photo` |

**Security Workflow:**
- Sensitive changes (Email/Password) trigger secondary validation.
- Profile photos are stored in `media/profile_photos/` with auto-generation of unique filenames.

**Account Deletion** (`/account/delete/`):
```python
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()  # Cascades to delete all related data
```

---

## 20. Help & Support Center

| Property | Details |
|----------|---------|
| **URL** | `/help/` |
| **Template** | `help.html` |
| **View Function** | `help_view()` in `views.py` (Line 960) |
| **URL Name** | `help` |

#### How It Works:

1. **FAQ Section**: Pre-defined frequently asked questions:
   ```python
   faqs = [
       {'q': 'How do I change my password?', 'a': 'Go to Settings...'},
       {'q': 'How do I cancel my subscription?', 'a': 'Navigate to Membership...'},
       {'q': 'Can I export my data?', 'a': 'Yes, go to Reports -> Download Data.'},
   ]
   ```

2. **Submit Support Ticket**: Users fill `HelpTicketForm` (subject + message):
   ```python
   ticket = form.save(commit=False)
   ticket.user = request.user
   ticket.save()
   ```

3. **View Past Tickets**: Shows all tickets submitted by the user:
   ```python
   user_tickets = HelpTicket.objects.filter(user=request.user)
   ```
   - Each ticket shows: Subject, Message, Status (Pending/Resolved), Admin Response (if resolved)

4. **Admin Response Flow**: When admin responds (from Admin Dashboard), the `HelpTicket.admin_response` is filled and `is_resolved=True` is set → user can see the response on their help page.

---

## 21. Sidebar Navigation

The sidebar is organized into **5 sections** with clear categorization:

### Section: Main

| Link | Icon | URL | Purpose |
|------|------|-----|---------|
| **Home** (active) | `fa-house` | `/dashboard/user/` | Dashboard home |
| **Progress** | `fa-chart-line` | `/progress/` | Analytics page |

### Section: Fitness

| Link | Icon | URL | Purpose |
|------|------|-----|---------|
| **My Workouts** | `fa-dumbbell` | `/workout/` | Browse workout plans |
| **Diet Plan** | `fa-utensils` | `/diet/` | Browse diet plans |
| **Nutrition** | `fa-droplet` | `/nutrition/` | Meal & water logging |
| **Vitality** | `fa-heart-pulse` | `/bmi/history/` | BMI history |
| **Goals** | `fa-bullseye` | `/goals/` | Goal tracking |
| **Exercise Videos** | `fa-film` | `/videos/` | Video tutorials |

### Section: Service

| Link | Icon | URL | Purpose |
|------|------|-----|---------|
| **Attendance** | `fa-calendar-check` | `/attendance/` | Mark & view attendance |
| **Membership** | `fa-crown` | `/membership/` | Subscription management |

### Section: Connect

| Link | Icon | URL | Purpose |
|------|------|-----|---------|
| **Trainers** | `fa-user-tie` | `/trainers/` | Browse & hire trainers |
| **Messages** | `fa-comments` | `/messages/` | Chat with trainers |
| **Community** | `fa-users` | `/community/` | Social forum |
| **Neural Hub** | `fa-brain` | `/ai-hub/` | AI features hub |

### Section: Account

| Link | Icon | URL | Purpose |
|------|------|-----|---------|
| **Admin Portal** | `fa-user-shield` | `/admin/` | Only visible for admin users |
| **Settings** | `fa-gear` | `/settings/` | Profile settings |
| **Help** | `fa-circle-question` | `/help/` | Support center |

### Sidebar Footer
- **Logout** button → POST form to `/logout/` with CSRF token

### Sidebar Profile Section
- Shows **profile photo** (clickable to change) + **username** + **subscription plan name**
- Photo upload uses hidden form that auto-submits on file selection:
  ```html
  <input type="file" onchange="document.getElementById('dashboard-photo-form').submit();">
  ```

---

## 22. Mobile Responsive Design

The User Dashboard is fully responsive with hamburger menu navigation on mobile.

### Breakpoint: ≤ 1024px

```css
.stats-row {
    grid-template-columns: 1fr;  /* Stack stat cards vertically */
}
.main-wrapper {
    padding: 2rem;  /* Reduce padding */
}
```

### Hamburger Menu System:

```javascript
function toggleSidebar() {
    sidebar.classList.toggle('open');
    overlay.classList.toggle('active');
    if (sidebar.classList.contains('open')) {
        hamburgerIcon.classList.replace('fa-bars', 'fa-xmark');
    } else {
        hamburgerIcon.classList.replace('fa-xmark', 'fa-bars');
    }
}

// Close sidebar when a nav link is clicked (on mobile)
document.querySelectorAll('.sidebar .nav-link').forEach(link => {
    link.addEventListener('click', () => {
        if (window.innerWidth <= 1024) {
            toggleSidebar();
        }
    });
});
```

**Special mobile feature**: Sidebar links auto-close the sidebar when clicked on mobile, improving the navigation experience.

---

## 24. FitSync Store (User & Admin)

The Store is a full-featured e-commerce module integrated into the FitSync ecosystem.

### User Shopping Experience (`/store/`)
- **Product Hub:** Categorized list of apparel, equipment, and recovery gear.
- **Cart Interface:** AJAX-powered quantity updates and item removal.
- **Checkout Protocol:** Delivery information capture and order synthesis.
- **My Orders:** Portal to view past purchases and fulfillment status.

### Admin Store Panel (`/store/manage/`)
- **Catalog Control:** Add and edit products with image assets, prices, and stock levels.
- **Order Command:** Unified dashboard to see all user orders and update status (Pending → Shipped → Delivered).
- **Stock Tracking:** Automated badges for "Low Stock" and "Sale" items.

---

## 📋 Complete URL Reference (User-Facing)

| URL | Name | Method | Purpose |
|-----|------|--------|---------|
| `/login/` | `login` | GET/POST | User login |
| `/signup/` | `signup` | GET/POST | New registration |
| `/verify-otp/` | `verify_otp` | GET/POST | Email OTP verification |
| `/forgot-password/` | `forgot_password` | GET/POST | Reset password |
| `/logout/` | `logout` | POST | End session |
| `/dashboard/user/` | `user_dashboard` | GET/POST | Main dashboard |
| `/progress/` | `progress` | GET | Analytics & charts |
| `/workout/` | `workout_list` | GET | Workout programs |
| `/workout/session/<pk>/` | `workout_session` | GET | Single workout detail |
| `/diet/` | `diet_list` | GET | Diet plans |
| `/diet/<pk>/` | `diet_detail` | GET | Single diet detail |
| `/nutrition/` | `nutrition` | GET/POST | Meal & water tracker |
| `/api/nutrition/water/add/` | `add_water` | POST | AJAX water tracking |
| `/bmi/calculator/` | `bmi_calculator` | GET/POST | BMI calculator |
| `/bmi/history/` | `bmi_history` | GET | Past BMI records |
| `/goals/` | `goals` | GET/POST | Goal management |
| `/attendance/` | `attendance` | GET | Calendar & stats |
| `/attendance/mark/` | `attendance_mark` | POST | Manual check-in |
| `/api/attendance/mark/` | `mark_attendance_api` | POST | AJAX check-in |
| `/membership/` | `membership` | GET | Subscription info |
| `/subscription/` | `subscription_plans` | GET | View plans |
| `/payment/` | `payment` | GET/POST | Razorpay checkout |
| `/payment/trainer/<id>/` | `trainer_payment` | GET/POST | Hire trainer payment |
| `/trainers/` | `trainer_list` | GET | Browse trainers |
| `/messages/` | `messages` | GET/POST | Chat system |
| `/community/` | `community` | GET/POST | Forum |
| `/ai-hub/` | `ai_hub` | GET | AI features hub |
| `/chatbot/` | `chatbot` | GET | AI chatbot |
| `/api/chatbot/` | `chatbot_api` | POST | Chatbot AJAX API |
| `/ai-workout/` | `ai_workout` | GET | AI workout generator |
| `/ai-diet/` | `ai_diet` | GET | AI diet generator |
| `/videos/` | `video_gallery` | GET | Exercise videos |
| `/settings/` | `settings` | GET/POST | Profile settings |
| `/help/` | `help` | GET/POST | Support center |
| `/profile/` | `profile` | GET/POST | Profile page |
| `/account/delete/` | `delete_account` | POST | Delete account |

---

## 🔐 Subscription-Based Feature Access

| Feature | Unpaid User | Paid Member | Elite Member |
|---------|:-----:|:-------:|:--------:|
| Dashboard | ❌ | ✅ | ✅ |
| Workouts | ❌ | ✅ | ✅ |
| Diet Plans | ❌ | ✅ | ✅ |
| Attendance | ❌ | ✅ | ✅ |
| BMI History | ❌ | ✅ | ✅ |
| AI Chatbot | ❌ | ✅ | ✅ |
| Store Access| ✅ | ✅ | ✅ |
| AI Hub Tools| ❌ | ✅ | ✅ |

**Note:** The system uses a **Single Mandatory Plan** (₹199 / 3-Months). All paid members have equal "Elite" access to all features.

**How Feature Locking Works:**
```python
# In every premium view:
sub = UserSubscription.objects.filter(user=request.user, is_active=True).first()
if not sub or sub.plan.name == 'basic':
    messages.warning(request, "This feature requires Premium membership.")
    return redirect('membership')
```

---

> **Document Version**: 1.0  
> **Last Updated**: March 6, 2026  
> **Project**: FitSync Elite — Gym Management System  
> **Framework**: Django 5.x (Python) + HTML/CSS/JavaScript + Razorpay + Google Gemini AI
