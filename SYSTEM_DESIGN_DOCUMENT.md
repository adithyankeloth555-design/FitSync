# FitSync — Detailed System Design Document

**Project Title:** FitSync – Intelligent Fitness Management System  
**Version:** 1.0  
**Date:** February 26, 2026  
**Technology Stack:** Django 4.2 · Python · MySQL · HTML/CSS/JS · Google Gemini AI  

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Overview](#2-system-overview)
3. [Feasibility Study](#3-feasibility-study)
4. [System Architecture](#4-system-architecture)
5. [Module Design](#5-module-design)
6. [Data Flow Diagrams](#6-data-flow-diagrams)
7. [Database Design](#7-database-design)
8. [Entity-Relationship Diagram](#8-entity-relationship-diagram)
9. [Data Dictionary](#9-data-dictionary)
10. [User Interface Design](#10-user-interface-design)
11. [API Design](#11-api-design)
12. [Security Design](#12-security-design)
13. [Role-Based Access Control](#13-role-based-access-control)
14. [AI & Chatbot Subsystem](#14-ai--chatbot-subsystem)
15. [Subscription & Payment Subsystem](#15-subscription--payment-subsystem)
16. [Reporting Subsystem](#16-reporting-subsystem)
17. [Deployment Architecture](#17-deployment-architecture)
18. [Testing Strategy](#18-testing-strategy)
19. [Future Enhancements](#19-future-enhancements)

---

## 1. Introduction

### 1.1 Purpose

This document provides a comprehensive system design for **FitSync**, a full-stack web-based intelligent fitness management platform. The system enables gym members, personal trainers, and administrators to manage fitness activities, diet plans, workout programs, subscriptions, and communication within a unified ecosystem.

### 1.2 Scope

FitSync covers the following functional domains:

| Domain | Description |
|---|---|
| User Management | Registration, authentication, role-based profiles (Member, Trainer, Admin) |
| Fitness Tracking | BMI calculation, attendance logging, progress analytics |
| Nutrition Management | Diet plans, meal scheduling, daily nutrition logging, water intake tracking |
| Workout Management | Workout programs with difficulty levels, exercise video gallery |
| AI Integration | AI-powered chatbot (Gemini), AI workout generation, AI diet planning |
| Subscription & Payment | Tiered membership plans (Basic → Elite Lifetime), payment processing |
| Communication | In-app messaging, trainer feedback, community posts, notifications |
| Administration | Dashboard analytics, report generation, trainer management, help desk |

### 1.3 Definitions and Acronyms

| Term | Definition |
|---|---|
| MVT | Model-View-Template (Django's architectural pattern) |
| ORM | Object-Relational Mapping |
| RBAC | Role-Based Access Control |
| BMI | Body Mass Index |
| CRUD | Create, Read, Update, Delete |
| CSRF | Cross-Site Request Forgery |
| API | Application Programming Interface |
| SPA | Single Page Application |

### 1.4 Technology Stack

| Layer | Technology |
|---|---|
| Backend Framework | Django 4.2.27 (Python) |
| Database | MySQL 8.x (via `django.db.backends.mysql`) |
| Frontend | HTML5, CSS3 (custom design system), Vanilla JavaScript |
| AI Engine | Google Gemini Pro API (with local heuristic fallback) |
| Web Server | Django Development Server / Gunicorn (production) |
| Static Files | Django StaticFiles with `STATICFILES_DIRS` |
| Media Storage | Local filesystem (`/media/`) |

---

## 2. System Overview

### 2.1 System Context

FitSync is a three-tier web application serving three distinct user roles within a gym/fitness ecosystem:

```
┌─────────────────────────────────────────────────────┐
│                   EXTERNAL SYSTEMS                   │
│          Google Gemini AI API  ·  Email SMTP          │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│               FITSYNC APPLICATION                    │
│  ┌─────────┐  ┌───────────┐  ┌──────────────────┐   │
│  │  Member  │  │  Trainer  │  │  Administrator   │   │
│  │  Portal  │  │  Portal   │  │     Portal       │   │
│  └────┬─────┘  └─────┬─────┘  └────────┬─────────┘   │
│       └──────────────┼─────────────────┘             │
│              ┌───────▼───────┐                       │
│              │  Django MVT   │                       │
│              │   Engine      │                       │
│              └───────┬───────┘                       │
│              ┌───────▼───────┐                       │
│              │   MySQL DB    │                       │
│              └───────────────┘                       │
└─────────────────────────────────────────────────────┘
```

### 2.2 High-Level Functional Decomposition

```
FitSync System
├── Authentication Module
│   ├── Member Login / Signup
│   ├── Trainer Login
│   ├── Admin Login
│   ├── Password Reset
│   └── Logout
├── Dashboard Module
│   ├── Admin Dashboard (analytics, user management)
│   ├── Trainer Dashboard (member management, feedback)
│   └── User Dashboard (overview, quick actions)
├── Fitness Tracking Module
│   ├── BMI Calculator & History
│   ├── Attendance Tracker (calendar, check-in)
│   ├── Progress Analytics (charts, weekly stats)
│   └── Goal Setting & Tracking
├── Nutrition Module
│   ├── Diet Plan Management (CRUD)
│   ├── Meal Scheduling (day-wise)
│   ├── Daily Nutrition Logger
│   └── Water Intake Tracker
├── Workout Module
│   ├── Workout Program Listing
│   ├── Workout Session View
│   ├── Exercise Video Gallery
│   └── Video Upload (Trainer)
├── AI Module
│   ├── AI Chatbot (Gemini / Local Fallback)
│   ├── AI Workout Generator
│   └── AI Diet Planner
├── Subscription Module
│   ├── Plan Management (5 tiers)
│   ├── Payment Processing
│   └── Feature Gating
├── Communication Module
│   ├── In-App Messaging
│   ├── Trainer Feedback & Ratings
│   ├── Community Forum (posts, comments)
│   └── System Notifications
├── Reports Module
│   ├── Attendance Reports
│   ├── Payment / Revenue Reports
│   ├── Member Reports
│   └── Data Export
└── Settings & Support Module
    ├── User Profile & Settings
    ├── Help Center (FAQs, Tickets)
    └── Account Deletion
```

---

## 3. Feasibility Study

### 3.1 Technical Feasibility

| Aspect | Assessment |
|---|---|
| Framework Maturity | Django 4.2 LTS — production-ready, extensively documented |
| Database | MySQL — industry-standard RDBMS, handles relational fitness data efficiently |
| AI Integration | Google Gemini API is production-ready; local fallback ensures zero downtime |
| Frontend | Server-rendered templates — no complex SPA framework needed |
| Hosting | Compatible with any Linux/Windows VPS, Docker-ready |

### 3.2 Operational Feasibility

- **Admin** manages the entire platform from a centralized dashboard
- **Trainers** are provisioned by admins and can manage their assigned members
- **Members** self-register and can access features based on subscription tier
- Intuitive UI reduces training overhead for gym staff

### 3.3 Economic Feasibility

| Component | Cost |
|---|---|
| Django Framework | Free (Open Source, BSD License) |
| MySQL Database | Free (Community Edition) |
| Google Gemini API | Free tier available; pay-as-you-go for production |
| Hosting (VPS) | ₹500–₹2,000/month |
| Domain + SSL | ₹500–₹1,000/year |
| **Total Annual Cost** | **~₹8,000–₹25,000** |

---

## 4. System Architecture

### 4.1 Architectural Pattern: MVT (Model-View-Template)

FitSync follows Django's **Model-View-Template** architecture:

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   Template   │◄──────│     View     │◄──────│    Model     │
│   (HTML/CSS/ │       │  (Business   │       │  (Database   │
│    JS)       │       │   Logic)     │       │   ORM)       │
└──────────────┘       └──────┬───────┘       └──────┬───────┘
                              │                      │
                       ┌──────▼───────┐       ┌──────▼───────┐
                       │  URL Router  │       │    MySQL     │
                       │  (urls.py)   │       │   Database   │
                       └──────────────┘       └──────────────┘
```

### 4.2 Application Structure

```
fitsync/                          # Project Root
├── fitsync/                      # Project Configuration
│   ├── settings.py               # Database, middleware, apps config
│   ├── urls.py                   # Root URL router
│   ├── wsgi.py                   # WSGI entry point
│   └── asgi.py                   # ASGI entry point
├── fitsync_app/                  # Primary Application
│   ├── models.py                 # 16 data models (256 lines)
│   ├── views.py                  # 72 view functions (1651 lines)
│   ├── views_help.py             # Help desk admin views
│   ├── urls.py                   # 97 URL patterns
│   ├── forms.py                  # 12 ModelForm classes
│   ├── admin.py                  # Django admin registrations
│   └── migrations/               # 28 migration files
├── subscriptions/                # Subscription Sub-Application
│   ├── models.py                 # SubscriptionPlan, UserSubscription
│   ├── forms.py                  # SubscriptionPlanForm
│   ├── admin.py                  # Admin with list_editable
│   └── migrations/               # 10 migration files
├── templates/fitsync_app/        # 55 HTML templates
├── static/
│   ├── css/                      # 5 stylesheets (gold.css, professional.css, etc.)
│   └── js/                       # 4 JS files (ai.js, chatbot.js, dashboard.js, main.js)
├── media/                        # User uploads
│   ├── profile_photos/
│   ├── exercise_videos/
│   ├── workout_files/
│   └── video_thumbnails/
├── schema.sql                    # MySQL schema with sample data
├── seed_db.py                    # Database seeding script
└── manage.py                     # Django management CLI
```

### 4.3 Request-Response Lifecycle

```
Browser Request
      │
      ▼
┌─────────────────────┐
│  Django Middleware   │  SecurityMiddleware → SessionMiddleware
│     Pipeline        │  → CsrfViewMiddleware → AuthenticationMiddleware
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  URL Resolution     │  fitsync/urls.py → fitsync_app/urls.py
│  (97 URL patterns)  │
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  View Function      │  @login_required decorator check
│  (views.py)         │  Role-based access validation
│                     │  Business logic execution
│                     │  Database queries via ORM
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  Template Rendering │  Context data → HTML Template
│  (55 templates)     │  Static files inclusion
└─────────┬───────────┘
          ▼
    HTML Response
```

---

## 5. Module Design

### 5.1 Authentication Module

**Purpose:** Manages user identity, session creation, and role-based routing.

| Function | URL Pattern | Method | Description |
|---|---|---|---|
| `login_view` | `/login/` | GET, POST | Member login with role-based redirect |
| `admin_login_view` | `/admin/login/` | GET, POST | Admin-only login with role verification |
| `trainer_login_view` | `/trainer/login/` | GET, POST | Trainer login (allows trainer + admin roles) |
| `signup_view` | `/signup/` | GET, POST | New member registration with validation |
| `forgot_password_view` | `/forgot-password/` | GET, POST | Password reset via username + email verification |
| `logout_view` | `/logout/` | GET | Session termination and redirect |

**Signup Validation Rules:**
- Password length: 8–12 characters
- Email: must be a valid `@gmail.com` address
- Username: must be unique
- Phone number: stored with country code prefix

**Login Flow:**
```
User submits credentials
      │
      ▼
authenticate(username, password)
      │
      ├── None → "Invalid credentials" error
      │
      ├── User found
      │      │
      │      ▼
      │   Check userprofile.role
      │      │
      │      ├── 'admin'   → redirect('/admin/')
      │      ├── 'trainer' → redirect('/dashboard/trainer/')
      │      └── 'member'  → redirect('/dashboard/user/')
      │
      └── UserProfile.DoesNotExist → redirect('/dashboard/user/')
```

### 5.2 Dashboard Module

**Three distinct dashboards serve each role:**

#### Admin Dashboard (`/admin/`)
- **Total Users:** Count of members (excludes trainers/admins)
- **Active Trainers:** Count of trainer-role profiles
- **Total Revenue:** Sum of successful payments
- **Membership Tier Distribution:** Breakdown by plan (Basic, Premium, Elite, Lifetime)
- **Recent Users Table:** Last 5 registered members

#### Trainer Dashboard (`/dashboard/trainer/`)
- **Assigned Members List:** Users with `assigned_trainer = current_user`
- **Attendance Rate:** Per-member 30-day attendance percentage
- **Feedback System:** Submit text feedback + 1–5 star rating per member
- **Auto-Notification:** Creates notification for member when feedback is submitted
- **Profile Photo Update:** Direct upload from dashboard
- **Stats Cards:** Total members, today's attendance, unread messages

#### User Dashboard (`/dashboard/user/`)
- **Trainer Assignment Section:** Displays assigned trainer (hidden for Basic plan)
- **Recent Feedback:** Last 5 trainer feedback entries
- **Quick Actions:** Links to all major features
- **Profile Photo Upload:** Direct from dashboard
- **Subscription Status:** Current plan display

### 5.3 Fitness Tracking Module

#### BMI Calculator (`/bmi/calculator/`)
- Input: weight (kg) and height (cm)
- Formula: `BMI = weight / (height/100)²`
- Records saved to `BMIHistory` model
- Classification: Underweight / Normal / Overweight / Obese

#### BMI History (`/bmi/history/`)
- Chronological list of all BMI records
- Trend visualization data

#### Attendance Tracker (`/attendance/`)
- **Calendar View:** Monthly grid with present/absent indicators
- **14-Day Status Strip:** Visual daily attendance overview
- **Attendance Rate:** `(days_present / current_day_of_month) × 100`
- **Check-In API:** `POST /api/attendance/mark/` — one check-in per day
- **Real-time Status:** Checks if already checked in today

#### Progress Analytics (`/progress/`)
- **Weekly Activity Chart:** 7-day attendance bar chart (height scaled to max count)
- **Weight History Chart:** Last 7 BMI records plotted chronologically
- **Metrics:** Weekly attendance count, total attendance, estimated calories burned (400/session), training duration (60 min/session), derived steps count
- **Weight Change:** Difference between first and last BMI record

#### Goals (`/goals/`)
- CRUD for personal fitness goals
- Categories: Weight Loss, Muscle Gain, Endurance/Cardio, Nutrition, Other
- Progress tracking: `current_value / target_value × 100`
- Toggle completion status
- Target date scheduling

### 5.4 Nutrition Module

#### Diet Plan Management
| Operation | URL | Access |
|---|---|---|
| List all plans | `/diet/` | All authenticated users |
| View plan details + meals | `/diet/<id>/` | All authenticated users |
| Create new plan | `/diet/add/` | Trainers |
| Edit plan | `/diet/<id>/edit/` | Trainers |
| Delete plan | `/diet/<id>/delete/` | Trainers |
| Add meal to plan | `/diet/<id>/meal/add/` | Trainers |
| Delete meal | `/meal/<id>/delete/` | Trainers |

**Meal Scheduling:** Each meal is assigned to a specific day (Monday–Sunday) with time, calories, protein, carbs, and fats.

#### Daily Nutrition Logger (`/nutrition/`)
- Log individual food items with full macro breakdown
- Daily totals auto-calculated
- Progress against daily goals (2000 cal, 150g protein, 250g carbs)
- Remaining macros display

#### Water Intake Tracker
- AJAX-based water logging via `POST /api/nutrition/water/add/`
- Daily goal: 2000ml (8 glasses × 250ml)
- Running total with progress percentage

### 5.5 Workout Module

| Feature | URL | Description |
|---|---|---|
| Workout List | `/workout/` | All programs with difficulty badges |
| Workout Session | `/workout/session/<id>/` | Detailed workout view |
| Add Workout | `/workout/add/` | Trainer creates new program |
| Video Gallery | `/videos/` | Exercise tutorial library |
| Video Upload | `/videos/upload/` | Trainer-only video upload |
| Video Delete | `/videos/delete/<id>/` | Owner or admin deletion |

**Difficulty Levels:** Beginner, Intermediate, Advanced  
**File Support:** Workout asset files, video files, video thumbnails

### 5.6 Communication Module

#### Messaging (`/messages/`)
- Contact list: Trainers see assigned trainees; Members see trainers/admins
- Includes past conversation partners (even if assignment changed)
- Real-time conversation thread per contact
- Message model: sender, receiver, subject, body, is_read, timestamp

#### Community Forum (`/community/`)
- Members create posts with optional image uploads
- Comments on posts (nested under `CommunityPost`)
- Chronological feed display

#### Notifications
- System-generated alerts (e.g., trainer submits feedback)
- Read/unread status tracking
- Ordered by creation time (newest first)

---

## 6. Data Flow Diagrams

### 6.1 Level 0 — Context Diagram

```
                    ┌──────────┐
   Login/Signup     │          │  Dashboard Data
   ───────────────► │          │ ◄───────────────
                    │          │
   Fitness Data     │  FitSync │  Reports
   ───────────────► │  System  │ ◄───────────────
                    │          │
   Payments         │          │  Notifications
   ───────────────► │          │ ◄───────────────
                    │          │
   AI Queries       │          │  AI Responses
   ───────────────► │          │ ◄───────────────
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │  MySQL   │
                    │ Database │
                    └──────────┘
```

### 6.2 Level 1 — Major Processes

```
┌─────────┐     ┌───────────────┐     ┌──────────────┐
│  User   │────►│ 1.0 Auth      │────►│ User Session │
└─────────┘     └───────────────┘     └──────────────┘
                       │
                       ▼
               ┌───────────────┐
               │ 2.0 Dashboard │◄──── Role Routing
               └───────┬───────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
   ┌─────────────┐ ┌────────┐ ┌──────────┐
   │3.0 Fitness  │ │4.0 Diet│ │5.0 Subs  │
   │  Tracking   │ │& Meals │ │& Payment │
   └─────────────┘ └────────┘ └──────────┘
          │            │            │
          ▼            ▼            ▼
   ┌──────────────────────────────────────┐
   │           MySQL Database             │
   └──────────────────────────────────────┘
```

### 6.3 Level 2 — Attendance Subsystem

```
Member ──► [Check-In Request] ──► attendance_mark_view()
                                        │
                            ┌───────────┼──────────┐
                            ▼           ▼          ▼
                      Validate     Check if     Create
                      Session    already done   Attendance
                                  today         Record
                                                   │
                                                   ▼
                                            attendance DB
                                                   │
                                                   ▼
                                          attendance_tracker_view()
                                                   │
                                    ┌──────────────┼──────────┐
                                    ▼              ▼          ▼
                              Calendar Grid   14-Day Strip  Rate Calc
```

---

## 7. Database Design

### 7.1 Database Configuration

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fitsync_db',
        'USER': 'root',
        'PASSWORD': '****',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 7.2 Table Summary

| # | Model | Table Name | Key Fields | Relationships |
|---|---|---|---|---|
| 1 | User (Django built-in) | `auth_user` | id, username, email, password | — |
| 2 | UserProfile | `fitsync_app_userprofile` | role, fitness_goal, weight, height, phone, specialty, price | OneToOne → User; FK → User (assigned_trainer) |
| 3 | DietPlan | `fitsync_app_dietplan` | name, daily_calories, protein, carbs, fats | FK → User (trainer) |
| 4 | Meal | `fitsync_app_meal` | day, name, calories, protein, carbs, fats, time | FK → DietPlan |
| 5 | WorkoutProgram | `fitsync_app_workoutprogram` | title, difficulty, frequency, asset_file | FK → User (trainer) |
| 6 | BMIHistory | `fitsync_app_bmihistory` | weight_kg, height_cm, bmi_score, recorded_at | FK → User |
| 7 | Attendance | `fitsync_app_attendance` | workout_type, notes, logged_at | FK → User |
| 8 | Payment | `fitsync_app_payment` | transaction_id, amount, status, payment_date | FK → User; FK → User (trainer) |
| 9 | Notification | `fitsync_app_notification` | title, message, is_read | FK → User |
| 10 | Goal | `fitsync_app_goal` | title, category, current_value, target_value, unit, target_date | FK → User |
| 11 | NutritionLog | `fitsync_app_nutritionlog` | date, meal_type, food_item, calories, protein, carbs, fats | FK → User |
| 12 | WaterLog | `fitsync_app_waterlog` | date, amount_ml | FK → User |
| 13 | Message | `fitsync_app_message` | subject, body, is_read, sent_at | FK → User (sender); FK → User (receiver) |
| 14 | TrainerFeedback | `fitsync_app_trainerfeedback` | feedback_text, rating (1–5) | FK → User (trainer); FK → User (member) |
| 15 | CommunityPost | `fitsync_app_communitypost` | content, image | FK → User (author) |
| 16 | CommunityComment | `fitsync_app_communitycomment` | content | FK → CommunityPost; FK → User |
| 17 | ExerciseVideo | `fitsync_app_exercisevideo` | title, description, video_file, thumbnail | FK → User (trainer) |
| 18 | HelpTicket | `fitsync_app_helpticket` | subject, message, is_resolved, admin_response | FK → User |
| 19 | SubscriptionPlan | `subscriptions_subscriptionplan` | name, price, annual_price, features | — |
| 20 | UserSubscription | `subscriptions_usersubscription` | start_date, expiry_date, is_active | OneToOne → User; FK → SubscriptionPlan |

---

## 8. Entity-Relationship Diagram

```
┌──────────────┐    1:1     ┌──────────────────┐
│   auth_user  │───────────►│   UserProfile    │
│  (Django)    │            │  role, specialty  │
└──────┬───────┘            │  assigned_trainer─┼──┐
       │                    └──────────────────┘  │
       │  1:N                      ▲              │
       │                           │ FK (self)    │
       ├───────────────────────────┘              │
       │                                          │
       │  1:N    ┌──────────────┐                 │
       ├────────►│  BMIHistory  │                 │
       │         └──────────────┘                 │
       │  1:N    ┌──────────────┐                 │
       ├────────►│  Attendance  │                 │
       │         └──────────────┘                 │
       │  1:N    ┌──────────────┐                 │
       ├────────►│   Payment    │◄── FK(trainer)──┘
       │         └──────────────┘
       │  1:N    ┌──────────────┐   1:N  ┌────────┐
       ├────────►│   DietPlan   │───────►│  Meal  │
       │         └──────────────┘        └────────┘
       │  1:N    ┌──────────────────┐
       ├────────►│  WorkoutProgram  │
       │         └──────────────────┘
       │  1:N    ┌──────────────┐
       ├────────►│     Goal     │
       │         └──────────────┘
       │  1:N    ┌──────────────┐
       ├────────►│ NutritionLog │
       │         └──────────────┘
       │  1:N    ┌──────────────┐
       ├────────►│   WaterLog   │
       │         └──────────────┘
       │  1:N    ┌──────────────┐
       ├────────►│ Notification │
       │         └──────────────┘
       │         ┌──────────────┐
       ├────────►│   Message    │◄── FK(receiver)
       │ sender  └──────────────┘
       │         ┌──────────────────┐
       ├────────►│ TrainerFeedback  │◄── FK(user)
       │ trainer └──────────────────┘
       │         ┌──────────────────┐   1:N  ┌───────────────────┐
       ├────────►│  CommunityPost   │───────►│ CommunityComment  │
       │         └──────────────────┘        └───────────────────┘
       │  1:N    ┌──────────────────┐
       ├────────►│  ExerciseVideo   │
       │         └──────────────────┘
       │  1:N    ┌──────────────┐
       ├────────►│  HelpTicket  │
       │         └──────────────┘
       │  1:1    ┌──────────────────┐   N:1  ┌──────────────────┐
       └────────►│ UserSubscription │───────►│ SubscriptionPlan │
                 └──────────────────┘        └──────────────────┘
```

**Key Relationships:**
- `UserProfile.assigned_trainer` → Self-referencing FK to `auth_user` (a trainer user)
- `Payment.trainer` → Optional FK to track which trainer received the payment
- `Message` has two FKs: `sender` and `receiver`, both to `auth_user`
- `TrainerFeedback` links trainer and member via two FKs to `auth_user`
- `UserSubscription` is OneToOne with User (one active subscription per user)

---

## 9. Data Dictionary

### 9.1 UserProfile

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | BigAutoField | PK, Auto | Primary key |
| user | OneToOneField | FK → auth_user, CASCADE | Link to Django User |
| role | CharField(20) | Choices: member/trainer/admin | User role in the system |
| fitness_goal | CharField(255) | Nullable | User's declared fitness goal |
| weight_kg | Decimal(5,2) | Nullable | Current body weight |
| height_cm | Decimal(5,2) | Nullable | Current height |
| profile_photo | ImageField | upload_to='profile_photos/' | Avatar image |
| phone_number | CharField(20) | Nullable | Phone with country code |
| address | TextField | Nullable | Mailing address |
| bio | TextField | Nullable | Personal bio |
| specialty | CharField(100) | Nullable | Trainer specialization |
| price | Decimal(10,2) | Default=50.00 | Monthly trainer price |
| assigned_trainer | ForeignKey | FK → auth_user, SET_NULL | Assigned personal trainer |
| created_at | DateTimeField | auto_now_add | Registration timestamp |

### 9.2 SubscriptionPlan

| Field | Type | Constraints | Description |
|---|---|---|---|
| name | CharField(50) | Unique, Choices | Plan tier identifier |
| price | Decimal(10,2) | Required | Monthly price in ₹ |
| annual_price | Decimal(10,2) | Nullable | Annual discounted price |
| duration_text | CharField(50) | Required | Display text ("Per Month", etc.) |
| description | TextField | Default text | Marketing description |
| features | TextField | Newline-separated | Feature checklist |
| is_active | BooleanField | Default=True | Whether plan is offered |

**Plan Tiers:**

| Plan Name | Display Name | Tier Level |
|---|---|---|
| basic | Basic | Entry-level, limited features |
| premium | Premium | Full features, personal trainers |
| gold | Premium Gold | Enhanced premium with extras |
| elite | Elite | All features, priority support |
| lifetime | Elite Lifetime | One-time payment, permanent access |

### 9.3 Payment

| Field | Type | Constraints | Description |
|---|---|---|---|
| user | ForeignKey | FK → auth_user | Paying member |
| trainer | ForeignKey | FK → auth_user, Nullable | Receiving trainer |
| transaction_id | CharField(100) | Unique | Payment reference |
| amount | Decimal(10,2) | Required | Amount in ₹ |
| status | CharField(20) | Choices: success/pending/failed | Payment state |
| payment_date | DateTimeField | auto_now_add | Transaction time |

---

## 10. User Interface Design

### 10.1 Design System

FitSync uses a custom CSS design system with 5 stylesheets:

| Stylesheet | Purpose |
|---|---|
| `gold.css` | Premium dark theme with gold accents (primary theme) |
| `professional.css` | Clean professional light theme variant |
| `dashboard.css` | Dashboard-specific layout and card styles |
| `forms.css` | Form input styling and validation states |
| `bmi.css` | BMI calculator-specific animations and gauge |

### 10.2 Template Inventory (55 Templates)

| Category | Templates | Count |
|---|---|---|
| Authentication | login, admin_login, trainer_login, signup, forgot_password, logout | 6 |
| Dashboards | admin_dashboard, trainer_dashboard, user_dashboard, home | 4 |
| Fitness | bmi_calculator, bmi_history, attendance, attendance_mark, attendance_view, progress, goals | 7 |
| Nutrition | diet_list, diet_detail, diet_add, diet_edit, meal_add, nutrition | 6 |
| Workout | workout_list, workout_session, workout_add, workout_edit | 4 |
| AI | chatbot, ai_hub, ai_workout, ai_diet | 4 |
| Subscription | subscription_plans, edit_subscription_plan, membership, payment, payment_trainer, payment_success | 6 |
| Communication | messages, community, help | 3 |
| Reports | report_attendance, report_payments, report_members, report_download | 4 |
| Management | trainer_list, add_trainer, trainer_member_progress, admin_help_tickets | 4 |
| Settings | profile, settings, video_gallery, video_upload | 4 |
| Layout | base.html (master template) | 1 |
| **Total** | | **53+** |

### 10.3 JavaScript Modules

| File | Functionality |
|---|---|
| `main.js` | Global utilities, navigation, responsive menu |
| `dashboard.js` | Dashboard chart rendering, real-time stat updates |
| `chatbot.js` | Chat interface, message history, AJAX API communication |
| `ai.js` | AI workout/diet generation, form handling |

---

## 11. API Design

### 11.1 REST-like API Endpoints

| Endpoint | Method | Auth | Description | Response |
|---|---|---|---|---|
| `/api/attendance/mark/` | POST | Required | Check-in for the day | JSON: status, message |
| `/api/chatbot/` | POST | Required | Send message to AI chatbot | JSON: reply text |
| `/api/nutrition/log/` | POST | Required | Log a meal from AI suggestions | JSON: status, message |
| `/api/nutrition/water/add/` | POST | Required | Add water intake | JSON: status, new_total |

### 11.2 API Request/Response Examples

**Chatbot API:**
```
POST /api/chatbot/
Content-Type: application/json

Request:  {"message": "How much protein do I need?"}
Response: {"reply": "**AI COACH DATABASE:** Protein is the foundational..."}
```

**Water Intake API:**
```
POST /api/nutrition/water/add/
Content-Type: application/json

Request:  {"amount": 250}
Response: {"status": "success", "new_total": 1500}
```

---

## 12. Security Design

### 12.1 Authentication Security

| Mechanism | Implementation |
|---|---|
| Password Hashing | Django's PBKDF2 with SHA256 (default) |
| Session Management | Server-side sessions via `django.contrib.sessions` |
| CSRF Protection | `CsrfViewMiddleware` — token validation on all POST requests |
| Clickjacking Protection | `X-Frame-Options: DENY` via `XFrameOptionsMiddleware` |
| Login Required | `@login_required` decorator on protected views |

### 12.2 Password Validation

Four validators enforced via `AUTH_PASSWORD_VALIDATORS`:
1. `UserAttributeSimilarityValidator` — prevents password similar to username/email
2. `MinimumLengthValidator` — minimum 8 characters (custom: 8–12 range enforced in signup)
3. `CommonPasswordValidator` — rejects common passwords
4. `NumericPasswordValidator` — prevents all-numeric passwords

### 12.3 Input Validation

| Input | Validation |
|---|---|
| Email | Regex: `^[a-z0-9._%+-]+@gmail\.com$` |
| Password | Length 8–12, confirmation match |
| Username | Uniqueness check against database |
| Phone | Country code prefix concatenation |
| File Uploads | Django's built-in file handling (ImageField, FileField) |

### 12.4 Access Control Checks

Every sensitive view performs explicit role verification:
```python
if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'admin':
    messages.error(request, "Access denied.")
    return redirect('admin_login')
```

---

## 13. Role-Based Access Control

### 13.1 Permission Matrix

| Feature | Member | Trainer | Admin |
|---|---|---|---|
| View own dashboard | ✅ | ✅ | ✅ |
| BMI Calculator | ✅ | ✅ | ✅ |
| Attendance (own) | ✅ | ✅ | ✅ |
| Diet Plans (view) | ✅ | ✅ | ✅ |
| Diet Plans (CRUD) | ❌ | ✅ | ✅ |
| Workout Programs (view) | ✅ | ✅ | ✅ |
| Workout Programs (create) | ❌ | ✅ | ✅ |
| AI Chatbot | ✅* | ✅ | ✅ |
| AI Workout/Diet Generator | ❌ (Premium+) | ✅ | ✅ |
| Personal Trainers | ❌ (Premium+) | — | ✅ |
| Video Upload | ❌ | ✅ | ❌ |
| Video Gallery (view) | ✅ | ✅ | ✅ |
| Community Forum | ✅ | ✅ | ✅ |
| Messaging | ✅ | ✅ | ✅ |
| Member Feedback | ❌ | ✅ | ❌ |
| View Member Progress | ❌ | ✅ | ✅ |
| Manage Trainers | ❌ | ❌ | ✅ |
| Manage Subscriptions | ❌ | ❌ | ✅ |
| View Reports | ❌ | Partial | ✅ |
| Help Ticket Resolution | ❌ | ❌ | ✅ |
| Account Deletion | ✅ | ✅ | ✅ |

*\* Basic plan members have limited AI access*

### 13.2 Feature Gating by Subscription

| Feature | Basic | Premium | Premium Gold | Elite | Lifetime |
|---|---|---|---|---|---|
| Core Fitness Tools | ✅ | ✅ | ✅ | ✅ | ✅ |
| AI Workout Generator | ❌ | ✅ | ✅ | ✅ | ✅ |
| AI Diet Planner | ❌ | ✅ | ✅ | ✅ | ✅ |
| Personal Trainer Access | ❌ | ✅ | ✅ | ✅ | ✅ |
| Trainer Dashboard Visibility | Hidden | ✅ | ✅ | ✅ | ✅ |

### 13.3 Strict Role Routing

Each dashboard enforces that the user belongs to the correct role. Mismatched roles are automatically redirected:

```
Admin accessing /dashboard/user/   → Redirected to /admin/
Trainer accessing /admin/          → Redirected to /dashboard/trainer/
Member accessing /dashboard/trainer/ → Redirected to /dashboard/user/
```

---

## 14. AI & Chatbot Subsystem

### 14.1 Architecture

```
User Message
      │
      ▼
┌─────────────────────────┐
│   chatbot_api_view()    │
│                         │
│  ┌─────────────────┐    │
│  │ Check Gemini    │    │
│  │ API Key Config  │    │
│  └────────┬────────┘    │
│           │              │
│     ┌─────▼─────┐       │
│     │ API Key   │       │
│     │ Valid?    │       │
│     └─────┬─────┘       │
│      Yes  │  No         │
│     ┌─────▼────┐  ┌─────▼──────────┐
│     │ Gemini   │  │ Local Heuristic│
│     │ Pro API  │  │ Knowledge Base │
│     │ Call     │  │ (35+ topics)   │
│     └─────┬────┘  └─────┬──────────┘
│           │              │
│           └──────┬───────┘
│                  ▼
│          JSON Response
└─────────────────────────┘
```

### 14.2 Local Knowledge Base Coverage

| Category | Topics |
|---|---|
| Nutrition | Protein, Carbs, Fats, Creatine, Calories, Water, Keto |
| Exercises | Squat, Deadlift, Bench, Push-up, Pull-up, Plank, Lunge, Burpee |
| Training Concepts | Hypertrophy, Strength, Cardio, HIIT, Rest/Sleep, Yoga, Stretching, Mobility |
| General Fitness | Weight Loss, Muscle Gain, Workout, Exercise, Diet, Nutrition, Motivation, Discipline, Soreness |

### 14.3 AI-Powered Features

| Feature | Endpoint | Subscription Requirement |
|---|---|---|
| AI Chatbot | `/chatbot/`, `/api/chatbot/` | All users (basic mode) |
| AI Workout Generator | `/ai-workout/` | Premium and above |
| AI Diet Planner | `/ai-diet/` | Premium and above |
| AI Hub | `/ai-hub/` | All users (portal) |

---

## 15. Subscription & Payment Subsystem

### 15.1 Payment Flow

```
Member selects plan
      │
      ▼
payment_view() / trainer_payment_view()
      │
      ├── Generate unique transaction_id (TXN-XXXXXX)
      │
      ├── Create Payment record (status='pending')
      │
      ├── Process payment
      │       │
      │       ├── Success → Update to 'success'
      │       │             Create/Update UserSubscription
      │       │             Set expiry_date
      │       │
      │       └── Failed → Update to 'failed'
      │
      └── Redirect to payment_success or error
```

### 15.2 Subscription Lifecycle

1. **Activation:** Payment success triggers `UserSubscription` creation
2. **Expiry Calculation:** Based on plan type — monthly (30 days), annual (365 days), or lifetime (36,500 days)
3. **Feature Gating:** Each view checks `UserSubscription.is_active` and `plan.name`
4. **Admin Control:** Admins can edit plan pricing, features, and active status from `/subscription/edit/<id>/`

### 15.3 Membership Dashboard (`/membership/`)

Displays:
- Current plan name, description, and features
- Validity period with days remaining
- Next billing amount
- Payment history table
- Available plan grid for upgrades

---

## 16. Reporting Subsystem

### 16.1 Available Reports (Admin Only)

| Report | URL | Data Source | Key Metrics |
|---|---|---|---|
| Attendance Report | `/reports/attendance/` | Attendance model | Daily average, peak time, engagement rate |
| Payment Report | `/reports/payments/` | Payment model | Total revenue, transaction list, status |
| Member Report | `/reports/members/` | UserProfile model | All members, registration date, profiles |
| Data Export | `/reports/download/` | Multiple | Downloadable data (planned) |

### 16.2 Admin Dashboard Analytics

| Metric | Calculation |
|---|---|
| Total Users | `UserProfile.objects.filter(role='member').count()` |
| Active Trainers | `UserProfile.objects.filter(role='trainer').count()` |
| Total Revenue | `Payment.objects.filter(status='success').aggregate(Sum('amount'))` |
| Tier Distribution | `UserSubscription.objects.values('plan__name').annotate(count=Count('id'))` |

---

## 17. Deployment Architecture

### 17.1 Development Environment

```
┌──────────────────────────────────────────┐
│          Developer Machine               │
│                                          │
│  ┌──────────────────────────────────┐    │
│  │  Django Development Server       │    │
│  │  python manage.py runserver      │    │
│  │  Port: 8000                      │    │
│  └──────────────┬───────────────────┘    │
│                 │                        │
│  ┌──────────────▼───────────────────┐    │
│  │  MySQL Server (localhost:3306)   │    │
│  │  Database: fitsync_db            │    │
│  └──────────────────────────────────┘    │
│                                          │
│  Static Files: /static/ (served by Django)│
│  Media Files:  /media/ (served by Django) │
└──────────────────────────────────────────┘
```

### 17.2 Production Architecture (Recommended)

```
┌───────────┐     ┌──────────────┐     ┌──────────────┐
│  Client   │────►│  Nginx       │────►│  Gunicorn    │
│  Browser  │     │  (Reverse    │     │  (WSGI)      │
└───────────┘     │   Proxy +    │     │  Workers: 4  │
                  │   Static)    │     └──────┬───────┘
                  └──────────────┘            │
                                       ┌─────▼────────┐
                                       │  Django App  │
                                       │  (FitSync)   │
                                       └──────┬───────┘
                                              │
                                       ┌──────▼───────┐
                                       │  MySQL 8.x   │
                                       │  (Dedicated) │
                                       └──────────────┘
                                              │
                                       ┌──────▼───────┐
                                       │  Media/Static│
                                       │  (CDN or S3) │
                                       └──────────────┘
```

### 17.3 Configuration Summary

| Setting | Development | Production |
|---|---|---|
| `DEBUG` | `True` | `False` |
| `ALLOWED_HOSTS` | `[]` | `['yourdomain.com']` |
| `SECRET_KEY` | Hardcoded | Environment variable |
| `DATABASE` | MySQL localhost | MySQL dedicated instance |
| `STATIC_ROOT` | Not set | `/var/www/static/` |
| `MEDIA_ROOT` | `BASE_DIR / 'media'` | S3 or dedicated storage |
| `GEMINI_API_KEY` | `YOUR_API_KEY_HERE` | Environment variable |

---

## 18. Testing Strategy

### 18.1 Testing Layers

| Layer | Scope | Tools |
|---|---|---|
| Unit Testing | Models, Forms, Utilities | Django TestCase, pytest |
| View Testing | HTTP request/response validation | Django Client |
| Integration Testing | Full request lifecycle | Django LiveServerTestCase |
| UI Testing | Frontend interactions | Selenium WebDriver |
| Security Testing | CSRF, authentication bypass | Manual + OWASP ZAP |

### 18.2 Critical Test Cases

| Module | Test Case | Expected Result |
|---|---|---|
| Auth | Login with valid credentials | Redirect to role-based dashboard |
| Auth | Login with invalid credentials | Error message, stay on login page |
| Auth | Signup with duplicate username | "Username already taken" error |
| Auth | Signup with password < 8 chars | Validation error |
| Auth | Signup with non-Gmail email | Validation error |
| RBAC | Member accessing admin dashboard | Redirect to user dashboard |
| RBAC | Trainer accessing admin dashboard | Redirect to trainer dashboard |
| BMI | Calculate BMI with valid inputs | Correct BMI stored in history |
| Attendance | Check-in once per day | Success; second attempt blocked |
| Payment | Successful payment | Subscription activated, Payment record created |
| Chatbot | Query with known keyword | Relevant response from knowledge base |
| Chatbot | Query with Gemini API | AI-generated response |
| Subscription | Basic user accesses AI tools | Redirect to membership page |
| Trainer | Submit feedback to member | Feedback saved, notification created |
| Community | Create post with image | Post visible in community feed |
| Account | Delete account | User and all related data removed |

### 18.3 Database Seeding for Testing

The project includes `seed_db.py` (14,201 bytes) for populating test data:
- Sample users (member, trainer, admin)
- Diet plans with meals
- Workout programs
- Attendance records
- Payment transactions
- Subscription assignments

---

## 19. Future Enhancements

### 19.1 Short-Term Improvements

| Enhancement | Priority | Effort |
|---|---|---|
| Email-based password reset (SMTP) | High | Medium |
| Real-time chat via WebSockets | High | High |
| PDF report generation & download | Medium | Medium |
| Mobile-responsive PWA wrapper | Medium | Low |
| Stripe/Razorpay payment gateway | High | Medium |

### 19.2 Medium-Term Roadmap

| Enhancement | Description |
|---|---|
| Wearable Integration | Sync with Fitbit, Apple Watch, Google Fit APIs |
| Advanced Analytics | Machine learning-based progress predictions |
| Multi-Gym Support | Franchise management with multi-tenant architecture |
| Workout Timer | Built-in interval timer with rest period alerts |
| Social Features | Friend system, challenge mode, leaderboards |

### 19.3 Long-Term Vision

| Enhancement | Description |
|---|---|
| Mobile Native Apps | React Native iOS/Android apps |
| Video Conferencing | Live trainer-member workout sessions |
| Computer Vision | AI form correction via camera feed |
| Marketplace | Third-party trainer and nutritionist marketplace |
| Gamification | XP system, badges, achievement unlocks |

---

## Appendix A: URL Route Map (97 Patterns)

| # | URL | View | Name |
|---|---|---|---|
| 1 | `/login/` | login_view | login |
| 2 | `/trainer/login/` | trainer_login_view | trainer_login |
| 3 | `/admin/login/` | admin_login_view | admin_login |
| 4 | `/signup/` | signup_view | signup |
| 5 | `/forgot-password/` | forgot_password_view | forgot_password |
| 6 | `/logout/` | logout_view | logout |
| 7 | `/profile/` | profile_view | profile |
| 8 | `/` | home_view | home |
| 9 | `/admin/` | admin_dashboard_view | admin_dashboard |
| 10 | `/dashboard/trainer/` | trainer_dashboard_view | trainer_dashboard |
| 11 | `/dashboard/user/` | user_dashboard_view | user_dashboard |
| 12 | `/trainers/` | trainer_list_view | trainer_list |
| 13 | `/trainers/add/` | add_trainer_view | add_trainer |
| 14 | `/trainers/delete/<id>/` | delete_trainer_view | delete_trainer |
| 15 | `/progress/` | progress_view | progress |
| 16 | `/attendance/` | attendance_tracker_view | attendance |
| 17 | `/membership/` | membership_view | membership |
| 18 | `/nutrition/` | nutrition_view | nutrition |
| 19 | `/goals/` | goals_view | goals |
| 20 | `/messages/` | messages_view | messages |
| 21 | `/settings/` | settings_view | settings |
| 22 | `/help/` | help_view | help |
| 23 | `/community/` | community_view | community |
| 24 | `/diet/` | diet_list_view | diet_list |
| 25 | `/diet/<id>/` | diet_detail_view | diet_detail |
| 26 | `/diet/add/` | diet_add_view | diet_add |
| 27 | `/diet/<id>/edit/` | diet_edit_view | diet_edit |
| 28 | `/diet/<id>/delete/` | diet_delete_view | diet_delete |
| 29 | `/diet/<id>/meal/add/` | meal_add_view | meal_add |
| 30 | `/meal/<id>/delete/` | meal_delete_view | meal_delete |
| 31 | `/workout/` | workout_list_view | workout_list |
| 32 | `/workout/session/<id>/` | workout_session_view | workout_session |
| 33 | `/workout/add/` | workout_add_view | workout_add |
| 34 | `/bmi/calculator/` | bmi_calculator_view | bmi_calculator |
| 35 | `/bmi/history/` | bmi_history_view | bmi_history |
| 36 | `/attendance/mark/` | attendance_mark_view | attendance_mark |
| 37 | `/api/attendance/mark/` | mark_attendance_api | mark_attendance_api |
| 38 | `/subscription/` | subscription_plans_view | subscription_plans |
| 39 | `/payment/` | payment_view | payment |
| 40 | `/payment/trainer/<id>/` | trainer_payment_view | trainer_payment |
| 41 | `/chatbot/` | chatbot_view | chatbot |
| 42 | `/ai-hub/` | ai_hub_view | ai_hub |
| 43 | `/api/chatbot/` | chatbot_api_view | chatbot_api |
| 44 | `/ai-workout/` | ai_workout_view | ai_workout |
| 45 | `/ai-diet/` | ai_diet_view | ai_diet |
| 46 | `/reports/attendance/` | report_attendance_view | report_attendance |
| 47 | `/reports/payments/` | report_payments_view | report_payments |
| 48 | `/reports/members/` | report_members_view | report_members |
| 49 | `/videos/` | video_gallery_view | video_gallery |
| 50 | `/videos/upload/` | video_upload_view | video_upload |
| 51 | `/admin/help-tickets/` | admin_help_tickets_view | admin_help_tickets |
| 52 | `/account/delete/` | delete_account_view | delete_account |

---

## Appendix B: Model Field Count Summary

| Model | Total Fields | ForeignKeys | File Fields |
|---|---|---|---|
| UserProfile | 14 | 2 | 1 (profile_photo) |
| DietPlan | 8 | 1 | 0 |
| Meal | 8 | 1 | 0 |
| WorkoutProgram | 7 | 1 | 1 (asset_file) |
| BMIHistory | 5 | 1 | 0 |
| Attendance | 4 | 1 | 0 |
| Payment | 6 | 2 | 0 |
| Notification | 5 | 1 | 0 |
| Goal | 10 | 1 | 0 |
| NutritionLog | 8 | 1 | 0 |
| WaterLog | 3 | 1 | 0 |
| Message | 6 | 2 | 0 |
| TrainerFeedback | 5 | 2 | 0 |
| CommunityPost | 4 | 1 | 1 (image) |
| CommunityComment | 4 | 2 | 0 |
| ExerciseVideo | 6 | 1 | 2 (video, thumbnail) |
| HelpTicket | 7 | 1 | 0 |
| SubscriptionPlan | 7 | 0 | 0 |
| UserSubscription | 5 | 2 | 0 |
| **Total** | **~120** | **~25** | **~5** |

---

*Document prepared for FitSync v1.0 — February 2026*  
*Total pages: ~19 | Models: 20 | Views: 72 | Templates: 55 | URL Patterns: 97*

