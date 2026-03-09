# 🏋️ FitSync Elite — Admin & Trainer Dashboard Documentation

> **Complete Guide**: How every section works in the Admin Dashboard and Trainer Dashboard — from login to logout, backend logic, frontend display, and data flow.

---

## 📑 Table of Contents

1. [Admin Dashboard](#-admin-dashboard)
   - [Admin Login](#1-admin-login-page)
   - [Admin Dashboard Home](#2-admin-dashboard-home)
   - [User Management (Members Report)](#3-user-management-members-report)
   - [Trainer Management](#4-trainer-management)
   - [Subscription Plans Management](#5-subscription-plans-management)
   - [Financial Overview (Payments Report)](#6-financial-overview-payments-report)
   - [Help Ticket Management](#7-help-ticket-management)
   - [Attendance Reports](#8-attendance-reports)
2. [Trainer Dashboard](#-trainer-dashboard)
   - [Trainer Login](#1-trainer-login-page)
   - [Trainer Dashboard Home](#2-trainer-dashboard-home)
   - [Member Management Cards](#3-member-management-cards)
   - [Feedback System](#4-feedback-system-modal)
   - [Member Progress Analytics](#5-member-progress-analytics)
   - [Workout Plans](#6-workout-plans)
   - [Diet Plans](#7-diet-plans)
   - [Video Gallery (Upload Videos)](#8-video-gallery-upload-videos)
   - [Messaging System](#9-messaging-system)
3. [Sidebar Navigation](#-sidebar-navigation)
4. [Mobile Responsive Design](#-mobile-responsive-design)
5. [Role-Based Access Control](#-role-based-access-control)

---

## 🔴 ADMIN DASHBOARD

The Admin Dashboard is the **Command Center** of FitSync. It provides full control over users, trainers, subscriptions, payments, help tickets, and reports.

---

### 1. Admin Login Page

| Property | Details |
|----------|---------|
| **URL** | `/admin/login/` |
| **Template** | `admin_login.html` |
| **View Function** | `admin_login_view()` in `views.py` (Line 41) |
| **URL Name** | `admin_login` |

#### How It Works:

1. **User enters** their username and password on the login form.
2. **Backend authenticates** using Django's `authenticate()` function.
3. **Role check**: The view checks `user.userprofile.role == 'admin'`.
   - ✅ If the user is an admin → Logs them in via `login()` and redirects to `/admin/` (Admin Dashboard).
   - ❌ If the user exists but is NOT an admin → Shows error: *"Access denied. Admin credentials required."*
   - ❌ If credentials are invalid → Shows error: *"Invalid credentials."*
4. **Design**: Full-screen background image with a centered login card. The card has an "Admin Access" badge, admin-themed colors, and a link to go back to the Member Portal.

#### Key Code (views.py):
```python
def admin_login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=u, password=p)
        if user is not None:
            if user.userprofile.role == 'admin':
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Access denied. Admin credentials required.")
```

---

### 2. Admin Dashboard Home

| Property | Details |
|----------|---------|
| **URL** | `/admin/` |
| **Template** | `admin_dashboard.html` (655 lines) |
| **View Function** | `admin_dashboard_view()` in `views.py` (Line 239) |
| **URL Name** | `admin_dashboard` |
| **Access** | Only `role='admin'` users |

#### How It Works:

When the admin visits `/admin/`, the system:

1. **Role routing**: Checks the user's role:
   - If trainer → redirects to Trainer Dashboard
   - If member → redirects to User Dashboard
   - If not admin → redirects to Admin Login with error
2. **Fetches real-time stats** from the database:

#### Section A: Revenue & Membership Stats (Top Row — 5 Cards)

| Card | Data Source | How It's Calculated |
|------|-----------|---------------------|
| **Total Revenue** (₹) | `Payment` model | `Payment.objects.filter(status='success').aggregate(Sum('amount'))` — sums up all successful payments |
| **Elite Members** | `UserSubscription` model | Counts subscriptions where `plan__name = 'elite'` |
| **Premium Members** | `UserSubscription` model | Counts subscriptions where `plan__name = 'premium'` |
| **Basic Members** | `UserSubscription` model | Counts subscriptions where `plan__name = 'basic'` |
| **Lifetime Members** | `UserSubscription` model | Counts subscriptions where `plan__name = 'lifetime'` |

**Backend Logic:**
```python
membership_stats = UserSubscription.objects.values('plan__name').annotate(count=Count('id'))
tier_counts = {'basic': 0, 'premium': 0, 'elite': 0, 'lifetime': 0}
for stat in membership_stats:
    plan_name = stat['plan__name']
    if plan_name in tier_counts:
        tier_counts[plan_name] = stat['count']
```

Each card has a **colored left border** to visually distinguish tiers:
- 🟡 Elite → Gold (#FFD700)
- 🟠 Premium → Amber (#f59e0b)
- 🔵 Basic → Blue (#3b82f6)
- 🟣 Lifetime → Purple (#a855f7)

#### Section B: General Info Stats (Second Row — 2 Cards)

| Card | Data Source |
|------|-----------|
| **Total Registered Members** | `UserProfile.objects.filter(role='member').count()` — counts only members, not admins or trainers |
| **Professional Trainers** | `UserProfile.objects.filter(role='trainer').count()` |
| **System Status** | Always shows "Active" (static display) |

#### Section C: Administrative Control Center (Quick Actions)

Two action buttons are displayed:

| Button | Action | Where It Goes |
|--------|--------|---------------|
| **ONBOARD NEW TRAINER** | Orange button with `fa-user-plus` icon | Links to `/trainers/add/` (Add Trainer form) |
| **MANAGE COACHING NETWORK** | Outlined button with `fa-users-gear` icon | Links to `/trainers/` (Trainer List page) |

#### Section D: Recently Registered Users (Table)

| Column | Data |
|--------|------|
| **Name** | Profile photo + username (capitalized). If no photo, shows first letter avatar with gold background |
| **Email** | User's email address |
| **Status** | Badge showing "Active" (blue) or "Inactive" (gray) based on `user.is_active` |

**Data Source:**
```python
recent_users = UserProfile.objects.filter(role='member')
    .select_related('user')
    .order_by('-user__date_joined')[:5]
```
Shows the **5 most recently joined** members.

#### Section E: User Growth Chart

- Placeholder section with text: *"Chart data will appear here once sufficient history is available."*
- Uses a `.chart-container` div with 200px height.

#### Section F: Logout Button

- Red-themed logout button at the bottom center.
- Submits a POST form to `{% url 'logout' %}` with CSRF token for security.

---

### 3. User Management (Members Report)

| Property | Details |
|----------|---------|
| **URL** | `/reports/members/` |
| **Template** | `report_members.html` (537 lines) |
| **View Function** | `report_members_view()` in `views.py` (Line 1646) |
| **URL Name** | `report_members` |
| **Access** | Admin and Trainer roles only |

#### How It Works:

1. **Role Check**: Only `admin` or `trainer` roles can access. Others get redirected with "Access denied."
2. **Data Fetching**:
   ```python
   members = UserProfile.objects.filter(role='member')
       .select_related('user')
       .order_by('-created_at')
   ```
3. **Dynamic Sidebar**: The sidebar changes based on the user's role:
   - Admin sees: Dashboard, Users, Trainers, Subscriptions, Payments, Reports
   - Trainer sees: Dashboard, All Members, Workout Plans, Diet Plans, Upload Videos, Messages

#### UI Sections:

| Section | Description |
|---------|-------------|
| **Page Header** | Shows "Member Database" title + active record count badge |
| **Actions Bar** | Search input (client-side filtering) + "Export Data" button linking to `/reports/download/` |
| **Data Table** | Premium table showing: Member Profile (photo + name + email), Status (Active/Inactive badge), Role/Plan, Joined Date, Actions (Message, View Profile, Edit Settings for admins) |

#### Action Buttons Per Row:
- 💬 **Message** → Opens messaging with `?user_id=X` pre-selected
- 📇 **View Profile** → Profile card (placeholder link)
- ⚙️ **Edit Settings** → Admin-only gear icon (placeholder link)

---

### 4. Trainer Management

#### 4a. Trainer List Page

| Property | Details |
|----------|---------|
| **URL** | `/trainers/` |
| **Template** | `trainer_list.html` (354 lines) |
| **View Function** | `trainer_list_view()` in `views.py` (Line 469) |
| **URL Name** | `trainer_list` |
| **Access** | Admin can view all trainers. Members need Premium/Elite subscription. Basic members get redirected. |

**How It Works:**

1. **Subscription Check**: If the user is NOT admin and has no subscription or a Basic plan, they are redirected to the membership page with a warning.
2. **Fetches all trainers**: `UserProfile.objects.filter(role='trainer')`
3. **Checks current trainer**: Displays "Your Coach" badge if the member has already hired a trainer.

**Card Layout (Per Trainer):**

| Element | Description |
|---------|-------------|
| **Image** | 350px height trainer photo (from profile or placeholder) |
| **Overlay** | Trainer name (Cinzel serif font) + specialty |
| **Badge** | "Elite Coach" or "Your Coach" (green glow) |
| **Bio** | Trainer description text |
| **Phone** | Contact number |
| **Address** | Location info |
| **Price** | ₹X,XXX / month — Admin can edit inline with price input field |

**Admin Special Features:**
- ✏️ **Inline Price Editing**: Admin sees an input field with a checkmark button to update the price via POST
- ➕ **"ONBOARD NEW COACH"** button at the top
- 🗑️ **"Terminate"** red button to delete a trainer (with confirmation dialog)

**Price Update Backend:**
```python
if request.method == 'POST' and is_admin:
    profile_to_update = UserProfile.objects.get(id=trainer_id, role='trainer')
    profile_to_update.price = float(new_price)
    profile_to_update.save()
```

**Member Features:**
- 💰 **"Hire This Coach"** button → Goes to payment page `/payment/trainer/<id>/`
- 💬 **"Message Coach"** if already hired
- 🏋️ **"View Workouts"** → Goes to workout list
- ❓ **"Inquire"** → Goes to chatbot

#### 4b. Add Trainer Page

| Property | Details |
|----------|---------|
| **URL** | `/trainers/add/` |
| **Template** | `add_trainer.html` (216 lines) |
| **View Function** | `add_trainer_view()` in `views.py` (Line 283) |
| **URL Name** | `add_trainer` |
| **Access** | Admin only |

**Form Fields:**

| Field | HTML Input | Required |
|-------|-----------|----------|
| **Network ID (Username)** | `text` input | ✅ |
| **Communication (Email)** | `email` input | ✅ |
| **Specialty Protocol** | `text` input (e.g., "Hypertrophy Engineer") | ❌ |
| **Market Price (₹)** | `number` input (default: 4999) | ❌ |
| **Security Key (Password)** | `password` input (min 8 chars) | ✅ |

**How It Works:**
1. Admin fills the form and clicks "AUTHORIZE DEPLOYMENT"
2. Backend creates a new `User` object with `create_user()`
3. Creates associated `UserProfile` with `role='trainer'`, specialty, and price
4. Redirects to Trainer List with success message

```python
user = User.objects.create_user(username=u, email=e, password=p)
UserProfile.objects.create(user=user, role='trainer', specialty=sp, price=float(pr))
```

#### 4c. Delete Trainer

| Property | Details |
|----------|---------|
| **URL** | `/trainers/delete/<trainer_id>/` |
| **View Function** | `delete_trainer_view()` in `views.py` (Line 306) |
| **URL Name** | `delete_trainer` |

**How It Works:**
1. Gets the `UserProfile` with the given ID and `role='trainer'`
2. Deletes the associated `User` object (cascades to delete all related data)
3. Redirects to Trainer List with success message

---

### 5. Subscription Plans Management

| Property | Details |
|----------|---------|
| **URL** | `/subscription/` |
| **Template** | `subscription_plans.html` (621 lines, dual-view) |
| **View Function** | `subscription_plans_view()` in `views.py` (Line 1245) |
| **URL Name** | `subscription_plans` |
| **Access** | Admin sees management view, members see pricing cards |

#### How It Works (Admin View):

The template uses a **conditional block** `{% if user.is_authenticated and user.userprofile.role == 'admin' %}` to render different layouts:

- **Admin sees**: Full sidebar + management grid with editable plan cards
- **Members see**: Hero section + beautiful pricing cards with "Select Plan" buttons

**Admin Management Grid (Per Plan Card):**

| Element | Description |
|---------|-------------|
| **Status Pill** | "Active" (green) or "Inactive" (red) based on `plan.is_active` |
| **Plan Name** | `plan.get_name_display()` — human-readable name |
| **Price** | ₹XX,XXX in large gold text |
| **Meta** | Duration text + Annual price if applicable |
| **Description** | Plan description text |
| **Feature Tags** | Small tags for each feature from `plan.get_features_list()` |
| **Configure Button** | Gold "Modify Protocol" button → Links to `/subscription/edit/<plan_id>/` |

**Data Source:**
```python
if request.user.userprofile.role == 'admin':
    plans = SubscriptionPlan.objects.all().order_by('price')  # Shows ALL plans including inactive
else:
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')  # Only active
```

#### Edit Subscription Plan

| Property | Details |
|----------|---------|
| **URL** | `/subscription/edit/<plan_id>/` |
| **Template** | `edit_subscription_plan.html` |
| **View Function** | `edit_subscription_plan()` in `views.py` (Line 1258) |
| **URL Name** | `edit_subscription_plan` |

**How It Works:**
1. Uses Django `SubscriptionPlanForm` to render an edit form pre-filled with current plan data
2. Admin can modify: name, price, annual price, duration, description, features, active status
3. On submit, validates and saves the form, then redirects back to plans list

---

### 6. Financial Overview (Payments Report)

| Property | Details |
|----------|---------|
| **URL** | `/reports/payments/` |
| **Template** | `report_payments.html` (435 lines) |
| **View Function** | `report_payments_view()` in `views.py` (Line 1618) |
| **URL Name** | `report_payments` |
| **Access** | Admin only |

#### How It Works:

1. **Fetches all payments**: `Payment.objects.all().order_by('-payment_date')`
2. **Calculates total revenue**: `payments.aggregate(Sum('amount'))['amount__sum']`
3. **Pre-processes** payment data into a list of dictionaries for the template

**Displayed Data:**

| Section | Content |
|---------|---------|
| **Page Header** | "FINANCIAL OVERVIEW" title (Cinzel font) + description |
| **Revenue Card** | Monthly Revenue amount in gold (₹XX,XXX.XX) |
| **Transactions Table** | ID (monospace), User name, Amount (green), Date, Status badge |

**Status Badges:**
- ✅ **Success** → Green badge (`#dcfce7` bg, `#166534` text)
- ⏳ **Pending** → Yellow badge (`#fef9c3` bg, `#854d0e` text)
- ❌ **Failed** → Red badge (`#fee2e2` bg, `#991b1b` text)

---

### 7. Help Ticket Management

| Property | Details |
|----------|---------|
| **URL** | `/admin/help-tickets/` |
| **Template** | `admin_help_tickets.html` (325 lines) |
| **View Function** | `admin_help_tickets_view()` in `views_help.py` (Line 7) |
| **URL Name** | `admin_help_tickets` |
| **Access** | Admin only |

#### How It Works:

1. **Stats Bar** (3 cards):
   - Total Tickets: `all_tickets.count`
   - Pending Response: `pending_tickets.count` (where `is_resolved=False`)
   - Resolved: `resolved_tickets.count` (where `is_resolved=True`)

2. **Ticket Cards** — Each ticket shows:

| Element | Description |
|---------|-------------|
| **User Info** | Avatar + Full name + Submit date |
| **Status** | "Pending" (amber) or "Resolved" (green) badge |
| **Subject** | Ticket subject in bold |
| **Message** | User's message with gold left border and tertiary background |
| **Admin Response** | If resolved → Shows green-bordered admin response |
| **Response Form** | If pending → Textarea + "Send Response & Mark Resolved" button |

**Responding to a Ticket (POST):**
```python
if request.method == 'POST':
    ticket = get_object_or_404(HelpTicket, id=ticket_id)
    ticket.admin_response = admin_response
    ticket.is_resolved = True
    ticket.save()
```

**Ordering:** Unresolved tickets appear first, then sorted by creation date (newest first):
```python
all_tickets = HelpTicket.objects.all().order_by('is_resolved', '-created_at')
```

---

### 8. Attendance Reports

| Property | Details |
|----------|---------|
| **URL** | `/reports/attendance/` |
| **Template** | `report_attendance.html` (418 lines) |
| **View Function** | `report_attendance_view()` in `views.py` (Line 1547) |
| **URL Name** | `report_attendance` |
| **Access** | Admin only |

#### How It Works:

1. **Calculates real-time statistics** from the `Attendance` model (last 30 days):

| Stat Card | Calculation |
|-----------|-------------|
| **Daily Average** | Total check-ins ÷ 30 days |
| **Peak Time** | Most common check-in hour (formatted as "HH:MM AM/PM") |
| **Engagement Rate** | Users who checked in (last 7 days) ÷ Total members × 100% |

2. **User Activity Log Table**:
   - Columns: Timestamp, User, Gate/Location, Validation Status
   - Shows recent attendance records

**Peak Time Calculation:**
```python
hour_counts = {}
for attendance in recent_attendance:
    if attendance.check_in_time:
        hour = attendance.check_in_time.hour
        hour_counts[hour] = hour_counts.get(hour, 0) + 1
peak_hour = max(hour_counts, key=hour_counts.get)
```

---

## 🟢 TRAINER DASHBOARD

The Trainer Dashboard is the **Coaching Command Center** where trainers manage assigned members, send feedback, track progress, and communicate.

---

### 1. Trainer Login Page

| Property | Details |
|----------|---------|
| **URL** | `/trainer/login/` |
| **Template** | `trainer_login.html` (303 lines) |
| **View Function** | `trainer_login_view()` in `views.py` (Line 60) |
| **URL Name** | `trainer_login` |

#### How It Works:

1. Trainer enters username and password.
2. Backend authenticates and checks `user.userprofile.role in ['trainer', 'admin']`.
   - ✅ Trainers AND admins can access the trainer dashboard.
   - ❌ Regular members get: *"Access denied. Trainer credentials required."*
3. On success → Redirects to `/dashboard/trainer/`

**Special UI Elements:**
- Gold-themed trainer badge: "Trainer Portal"
- Info box explaining: *"This portal is exclusively for FitSync trainers."*
- Footer links: Forgot Password, Need Help
- **Login Mode Switcher**: Quick links to Member Login and Admin Login

---

### 2. Trainer Dashboard Home

| Property | Details |
|----------|---------|
| **URL** | `/dashboard/trainer/` |
| **Template** | `trainer_dashboard.html` (828 lines) |
| **View Function** | `trainer_dashboard_view()` in `views.py` (Line 322) |
| **URL Name** | `trainer_dashboard` |
| **Access** | Trainer role only |

#### How It Works:

1. **Role Routing**:
   - Admin → redirected to Admin Dashboard
   - Member → redirected to User Dashboard
   - Non-trainer → redirected to User Dashboard

2. **Profile Photo Upload (POST)**:
   - The sidebar has a camera icon overlay on the trainer's avatar
   - Clicking it triggers a hidden file input
   - Selecting a file auto-submits the form → saves new photo to `userprofile.profile_photo`

3. **Feedback Submission (POST)** — handled on the same URL (see [Feedback System](#4-feedback-system-modal))

#### Stats Cards (3 Cards):

| Card | Data Source | Calculation |
|------|-----------|-------------|
| **Active Athletes** | `members.count()` | Count of users where `userprofile.assigned_trainer == current_trainer` |
| **Daily Check-ins** | `Attendance` model | `Attendance.objects.filter(user__userprofile__assigned_trainer=request.user, logged_at__date=today).count()` |
| **Pending Messages** | `Message` model | `Message.objects.filter(receiver=request.user, is_read=False).count()` |

**Member Fetching (Optimized Query):**
```python
members = User.objects.filter(
    userprofile__assigned_trainer=request.user
).select_related('userprofile').annotate(
    last_attendance_date=Max('attendance_logs__logged_at'),
    attended_days_count=Count(
        'attendance_logs__logged_at__date',
        filter=Q(attendance_logs__logged_at__date__gte=thirty_days_ago),
        distinct=True
    )
)
```

The query uses **Django annotations** to efficiently fetch:
- Last attendance date
- Number of attended days in the last 30 days
- Attendance rate is calculated as `(attended_days / 30) × 100`

---

### 3. Member Management Cards

Each assigned member gets a **rich card** displayed in a responsive grid (`members-grid`).

#### Card Sections:

| Section | Content |
|---------|---------|
| **Header** | Member avatar (70px, gold border) + Full name + Email + Fitness Goal badge |
| **Performance Metrics** | Last Workout date, Attendance rate (%), Weight in kg |
| **Action Buttons** | Chat, Feedback, Analytics, Plan |

#### Action Buttons Explained:

| Button | Action | How It Works |
|--------|--------|-------------|
| 💬 **Chat** | Opens Messages page | Links to `/messages/?user_id=<member_id>` which pre-selects the conversation |
| ⭐ **Feedback** | Opens Feedback Modal | JavaScript event: `openFeedbackModal(userId, userName)` — passes member ID and name |
| 📊 **Analytics** | Opens Progress Page | Links to `/trainer/member/<member_id>/progress/` |
| 📋 **Plan** | Placeholder | Currently links to `#` (future feature) |

#### Empty State:
If no members are assigned, shows a large faded users icon with text: *"No members assigned yet."*

---

### 4. Feedback System (Modal)

The Feedback Modal allows trainers to rate and review a member's performance.

#### How It Works:

1. **Opening the Modal**: Clicking the "Feedback" button triggers JavaScript:
   ```javascript
   document.querySelectorAll('.btn-feedback').forEach(function(button) {
       button.addEventListener('click', function() {
           const userId = this.getAttribute('data-user-id');
           const userName = this.getAttribute('data-user-name');
           openFeedbackModal(userId, userName);
       });
   });
   ```

2. **Modal UI Elements:**
   - Athlete name displayed in gold
   - **Star Rating** (1-5 stars, interactive):
     ```javascript
     function setRating(rating) {
         document.getElementById('feedback_rating').value = rating;
         const stars = document.querySelectorAll('.rating-star');
         stars.forEach((star, index) => {
             if (index < rating) star.classList.add('active');
             else star.classList.remove('active');
         });
     }
     ```
   - **Detailed Analysis** textarea (required)
   - **"Send Evaluation"** submit button

3. **Backend Processing (POST to `/dashboard/trainer/`):**
   ```python
   if user_id and feedback_text:
       member = User.objects.get(id=user_id)
       TrainerFeedback.objects.create(
           trainer=request.user,
           user=member,
           feedback_text=feedback_text,
           rating=int(rating) if rating else None
       )
       # Also creates a Notification for the member
       Notification.objects.create(
           user=member,
           title='New Feedback from Your Trainer',
           message='Your trainer has provided feedback on your performance.'
       )
   ```

4. **Closing the Modal**: Click the × button, click outside the modal, or after submission.

---

### 5. Member Progress Analytics

| Property | Details |
|----------|---------|
| **URL** | `/trainer/member/<user_id>/progress/` |
| **Template** | `trainer_member_progress.html` (268 lines) |
| **View Function** | `trainer_member_progress_view()` in `views.py` (Line 605) |
| **URL Name** | `trainer_member_progress` |
| **Access** | Trainer and Admin only |

#### How It Works:

1. **Fetches member data**:
   ```python
   member = get_object_or_404(User, id=user_id)
   history = BMIHistory.objects.filter(user=member).order_by('recorded_at')
   ```

2. **Chart.js Interactive Graph** — Dual-axis line chart:
   - **Left Y-axis**: BMI Score (gold color, `#D4AF37`)
   - **Right Y-axis**: Weight in kg (green color, `#10B981`)
   - **X-axis**: Entry dates
   - Both lines use `tension: 0.4` for smooth curves
   - Gradient fill under each line

3. **History Table**:
   - Columns: Entry Date, Weight (kg), Height (cm), BMI Score (in a gold badge)
   - Data passed from template as JSON inside a hidden `div`:
   ```html
   <div id="progression-data" style="display: none;"
       data-history='[{"date": "Mar 01", "bmi": 24.5, "weight": 75.0}, ...]'>
   </div>
   ```

4. **Back button** → Returns to Trainer Dashboard

---

### 6. Workout Plans

| Property | Details |
|----------|---------|
| **URL** | `/workout/` |
| **URL Name** | `workout_list` |
| **Access** | Trainer sidebar link |

#### How It Works:
- Trainers can **create, view, and edit** workout programs
- Each workout has exercises with sets, reps, and instructions
- Accessible from the trainer sidebar menu

---

### 7. Diet Plans

| Property | Details |
|----------|---------|
| **URL** | `/diet/` |
| **URL Name** | `diet_list` |
| **Access** | Trainer sidebar link |

#### How It Works:
- Trainers can **create detailed diet plans** with multiple meals
- Each plan includes meal name, time, ingredients, calories, macros
- Full CRUD operations: Add, View, Edit, Delete diet plans and individual meals

---

### 8. Video Gallery (Upload Videos)

| Property | Details |
|----------|---------|
| **URL** | `/videos/` |
| **View Function** | `video_gallery_view()` in `views.py` (Line 1660) |
| **URL Name** | `video_gallery` |
| **Upload URL** | `/videos/upload/` |
| **Delete URL** | `/videos/delete/<pk>/` |

#### How It Works:

1. **Gallery View**: Shows all exercise videos uploaded by trainers, ordered by newest first
2. **Upload** (Trainer only):
   - Checks if user is trainer
   - Uses `ExerciseVideoForm` for file upload
   - Saves with `video.trainer = request.user`
3. **Delete** (Trainer who uploaded OR admin):
   - Verifies ownership or admin status before deletion

---

### 9. Messaging System

| Property | Details |
|----------|---------|
| **URL** | `/messages/` |
| **URL Name** | `messages` |

#### How It Works:
- Real-time chat between trainer and assigned members
- Accessed from sidebar or member card "Chat" button
- Pre-selects conversation when accessed with `?user_id=X` query parameter
- Tracks read/unread status for unread message count on dashboard

---

## 📱 Sidebar Navigation

### Admin Sidebar Menu Items:

| Menu Item | Icon | URL | Description |
|-----------|------|-----|-------------|
| Dashboard | `fa-gauge` | `/admin/` | Admin home with stats |
| Users | `fa-user` | `/reports/members/` | Member database |
| Trainers | `fa-table-cells` | `/trainers/` | Trainer management |
| Subscriptions | `fa-envelope` | `/subscription/` | Plan management |
| Payments | `fa-money-bill-transfer` | `/reports/payments/` | Financial overview |
| Help Tickets | `fa-headset` | `/admin/help-tickets/` | Support tickets |
| Reports ▼ | `fa-file-lines` | Expandable submenu | Collapsible sub-menu |
| → Members | `fa-users-viewfinder` | `/reports/members/` | Member reports |
| → Financials | `fa-file-invoice-dollar` | `/reports/payments/` | Payment reports |
| → Attendance | `fa-clipboard-user` | `/reports/attendance/` | Attendance reports |

**Reports Submenu Toggle:**
```javascript
function toggleSubmenu(id) {
    const el = document.getElementById(id);
    el.style.display = (el.style.display === 'none') ? 'block' : 'none';
}
```

### Trainer Sidebar Menu Items:

| Menu Item | Icon | URL | Description |
|-----------|------|-----|-------------|
| Dashboard | `fa-gauge` | `/dashboard/trainer/` | Trainer home |
| All Members | `fa-users` | `/reports/members/` | Full member list |
| Workout Plans | `fa-dumbbell` | `/workout/` | Manage workouts |
| Diet Plans | `fa-utensils` | `/diet/` | Manage diets |
| Upload Videos | `fa-film` | `/videos/` | Exercise video library |
| Messages | `fa-message` | `/messages/` | Chat with members |
| Logout | `fa-right-from-bracket` | POST to `/logout/` | End session |

---

## 📱 Mobile Responsive Design

Both dashboards implement full mobile responsiveness with three breakpoints:

### Breakpoint: ≤ 1024px (Tablet)

```css
.sidebar {
    transform: translateX(-100%);  /* Hidden off-screen */
}
.sidebar.open {
    transform: translateX(0);
    box-shadow: 10px 0 30px rgba(0, 0, 0, 0.5);
}
.main-area {
    margin-left: 0 !important;  /* Full width */
}
```

### Breakpoint: ≤ 768px (Mobile)

- Stats grids become single column
- Member cards stack vertically
- Page titles shrink to 1.5rem
- Padding reduces for more content space

### Hamburger Menu System:

1. **Hamburger Button** (`#hamburger-btn`): Positioned top-left with `fa-bars` icon
2. **Sidebar Overlay** (`#sidebar-overlay`): Semi-transparent backdrop when sidebar is open
3. **Toggle Logic**:
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
   hamburgerBtn.addEventListener('click', toggleSidebar);
   overlay.addEventListener('click', toggleSidebar);  // Click outside to close
   ```

---

## 🔐 Role-Based Access Control

FitSync uses a strict role-based system stored in `UserProfile.role`:

| Role | Can Access | Cannot Access |
|------|-----------|---------------|
| `admin` | Admin Dashboard, All Reports, Trainer Management, Subscription Management, Help Tickets | User Dashboard, Trainer Dashboard |
| `trainer` | Trainer Dashboard, Member List, Workout Plans, Diet Plans, Videos, Messages, Member Progress | Admin Dashboard, Payments, Subscriptions, Help Tickets |
| `member` | User Dashboard, Personal Stats, BMI, Attendance, Nutrition, AI Features, Help | Admin Dashboard, Trainer Dashboard |

### How Routing Works:

Every dashboard view has a **role routing block** at the top:

```python
@login_required
def admin_dashboard_view(request):
    if hasattr(request.user, 'userprofile'):
        if request.user.userprofile.role == 'trainer':
            return redirect('trainer_dashboard')
        elif request.user.userprofile.role == 'member':
            return redirect('user_dashboard')
    
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'admin':
        messages.error(request, "Access denied. Admin account required.")
        return redirect('admin_login')
```

This ensures:
- A trainer trying to access `/admin/` gets redirected to their dashboard
- A member trying to access `/dashboard/trainer/` gets redirected to their dashboard
- An unauthenticated user gets redirected to the login page (via `@login_required`)

---

## 📋 Summary of All URLs

### Admin URLs:

| URL Pattern | Name | Method | Purpose |
|-------------|------|--------|---------|
| `/admin/login/` | `admin_login` | GET/POST | Admin login form |
| `/admin/` | `admin_dashboard` | GET | Admin dashboard home |
| `/trainers/` | `trainer_list` | GET/POST | List + manage trainers |
| `/trainers/add/` | `add_trainer` | GET/POST | Onboard new trainer |
| `/trainers/delete/<id>/` | `delete_trainer` | GET | Remove a trainer |
| `/subscription/` | `subscription_plans` | GET | Manage subscription plans |
| `/subscription/edit/<id>/` | `edit_subscription_plan` | GET/POST | Edit a specific plan |
| `/reports/members/` | `report_members` | GET | Member database |
| `/reports/payments/` | `report_payments` | GET | Financial transactions |
| `/reports/attendance/` | `report_attendance` | GET | Attendance statistics |
| `/reports/download/` | `report_download` | GET | Export data as CSV |
| `/admin/help-tickets/` | `admin_help_tickets` | GET/POST | Support ticket management |

### Trainer URLs:

| URL Pattern | Name | Method | Purpose |
|-------------|------|--------|---------|
| `/trainer/login/` | `trainer_login` | GET/POST | Trainer login form |
| `/dashboard/trainer/` | `trainer_dashboard` | GET/POST | Trainer dashboard + feedback |
| `/trainer/member/<id>/progress/` | `trainer_member_progress` | GET | Member BMI/weight chart |
| `/workout/` | `workout_list` | GET | Browse workout programs |
| `/diet/` | `diet_list` | GET | Browse diet plans |
| `/videos/` | `video_gallery` | GET | Exercise video library |
| `/videos/upload/` | `video_upload` | GET/POST | Upload exercise video |
| `/messages/` | `messages` | GET/POST | Chat with members |

---

> **Document Version**: 1.0  
> **Last Updated**: March 6, 2026  
> **Project**: FitSync Elite — Gym Management System  
> **Framework**: Django (Python) with HTML/CSS/JavaScript frontend
