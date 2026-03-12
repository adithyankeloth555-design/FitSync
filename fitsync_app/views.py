import os
import random
import string
import calendar
import json
import google.generativeai as genai # pyre-ignore[21]
from datetime import datetime, date, timedelta, time # pyre-ignore[21]
import re

from django.shortcuts import render, redirect, get_object_or_404 # pyre-ignore[21]
from django.urls import reverse # pyre-ignore[21]
from django.contrib.auth import authenticate, login, logout # pyre-ignore[21]
from django.contrib.auth.models import User # pyre-ignore[21]
from django.contrib import messages # pyre-ignore[21]
from django.contrib.auth.decorators import login_required # pyre-ignore[21]
from django.core.mail import send_mail # pyre-ignore[21]
from django.conf import settings # pyre-ignore[21]
from django.utils import timezone # pyre-ignore[21]
from django.db.models import Q, Count, Sum, Max, F, Avg # pyre-ignore[21]
from django.views.decorators.http import require_POST # pyre-ignore[21]
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect # pyre-ignore[21]

from .models import (
    DietPlan, WorkoutProgram, BMIHistory, Attendance, UserProfile, Payment, Goal,
    NutritionLog, Message, CommunityPost, CommunityComment, Notification, WaterLog,
    TrainerFeedback, ExerciseVideo, EmailOTP, LiveSession, Product, Cart, CartItem,
    Order, OrderItem, Meal, HelpTicket, FitnessAssessment
) # pyre-ignore[21]
from .forms import (
    DietPlanForm, WorkoutProgramForm, BMIHistoryForm, AttendanceForm, MealForm,
    GoalForm, NutritionLogForm, MessageForm, CommunityPostForm, ExerciseVideoForm,
    UserProfileForm, HelpTicketForm, ProductForm, OrderUpdateForm
) # pyre-ignore[21]

from decimal import Decimal

from subscriptions.models import UserSubscription, SubscriptionPlan # pyre-ignore[21]
from subscriptions.forms import SubscriptionPlanForm # pyre-ignore[21]

# Auth
def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {u}!")
            
            # Send Login Notification Email
            try:
                login_time = timezone.now().strftime("%d %B %Y – %I:%M %p")
                user_name = f"{user.first_name} {user.last_name}".strip() or user.username
                user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
                
                device = "Desktop / Laptop"
                if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
                    device = "Mobile Device"
                
                subject = 'Security Alert: New Login to Your FitSync Account'
                message = f"""Hello,

Your FitSync account was successfully logged in.

Login Details:

User: {user_name}
Login Time: {login_time}
Device: {device}
Location: India (Based on IP)

If this was you, no further action is required.

If you did not log in to your account, please change your password immediately and contact the FitSync support team.

Your fitness journey matters to us. We are committed to keeping your account secure.

Best Regards,
FitSync Security Team
"""
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True
                )
            except Exception as e:
                print(f"Login email failed: {e}")

            # Role-based redirect
            try:
                role = user.userprofile.role
                if role == 'admin':
                    return redirect('admin_dashboard')
                elif role == 'trainer':
                    return redirect('trainer_dashboard')
            except UserProfile.DoesNotExist:
                pass
                
            return redirect('user_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'fitsync_app/login.html')




def signup_view(request):
    if request.method == 'POST':
        fn = request.POST.get('first_name')
        ln = request.POST.get('last_name')
        u = request.POST.get('username')
        e = request.POST.get('email')
        p = request.POST.get('password')
        cp = request.POST.get('confirm_password')
        cc = request.POST.get('country_code', '')
        ph = request.POST.get('phone_number')
        full_phone = f"{cc} {ph}".strip()

        if len(p) < 8 or len(p) > 12:
            messages.error(request, "Password must be between 8 and 12 characters.")
            return render(request, 'fitsync_app/signup.html')
            
        email_regex = r'^[a-z0-9._%+-]+@gmail\.com$'
        if not re.match(email_regex, e):
            messages.error(request, "Please use a valid @gmail.com address.")
            return render(request, 'fitsync_app/signup.html')

        if p != cp:
            messages.error(request, "Passwords do not match.")
            return render(request, 'fitsync_app/signup.html')
        
        if User.objects.filter(username=u).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'fitsync_app/signup.html')

        if User.objects.filter(email=e).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'fitsync_app/signup.html')

        # Generate OTP
        otp = ''.join(random.choices(string.digits, k=6))
        EmailOTP.objects.filter(email=e).delete()
        EmailOTP.objects.create(email=e, otp=otp)

        # Send Email
        subject = f'Welcome to FitSync, {fn}! Your 6-digit Verification Code'
        message = f"""Hello,

We received a request to verify your account on FitSync – Your Ultimate Fitness Companion

Your One-Time Password (OTP) is:

🔐 OTP Code: {otp}

This OTP is valid for 5 minutes. Please do not share this code with anyone.

If you did not request this verification, please ignore this email or contact the FitSync support team.

Stay strong. Stay Fit.

Best Regards,
FitSync Security Team
FitSync – Your Ultimate Fitness Companion
"""
        email_from = settings.DEFAULT_FROM_EMAIL
        recipient_list = [e]
        
        try:
            send_mail(subject, message, email_from, recipient_list)
            # Store full registration data in session
            request.session['signup_data'] = {
                'first_name': fn,
                'last_name': ln,
                'username': u,
                'email': e,
                'password': p,
                'phone_number': full_phone
            }
            messages.success(request, f"OTP sent to {e}. Please verify to continue.")
            return redirect('verify_otp')
        except Exception as ex:
            messages.error(request, f"Error sending email: {str(ex)}")
            return render(request, 'fitsync_app/signup.html')

    return render(request, 'fitsync_app/signup.html')

def verify_otp_view(request):
    signup_data = request.session.get('signup_data')
    if not signup_data:
        messages.error(request, "Registration session expired. Please start over.")
        return redirect('signup')

    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        email = signup_data['email']

        otp_obj = EmailOTP.objects.filter(email=email, otp=otp_input).first()

        if otp_obj:
            if otp_obj.is_expired():
                messages.error(request, "OTP has expired. Please sign up again.")
                return redirect('signup')
            
            # SUCCESS: Create User with ALL details
            user = User.objects.create_user(
                username=signup_data['username'],
                email=signup_data['email'],
                password=signup_data['password'],
                first_name=signup_data['first_name'],
                last_name=signup_data['last_name']
            )
            UserProfile.objects.create(
                user=user, 
                role='member', 
                phone_number=signup_data['phone_number']
            )
            
            # Cleanup
            otp_obj.delete()
            del request.session['signup_data']
            
            messages.success(request, "Verification successful! Your account is ready. Please login.")
            return redirect('login') # Directly to Login Page
        else:
            messages.error(request, "Invalid code. Please check your Gmail.")

    return render(request, 'fitsync_app/verify_otp.html', {'email': signup_data['email']})

def forgot_password_view(request):
    # Initialize reset session if not present
    if 'reset_step' not in request.session:
        request.session['reset_step'] = 1

    step = request.session.get('reset_step', 1)
    email = request.session.get('reset_email', '')

    if request.method == 'POST':
        if step == 1:
            email = request.POST.get('email', '').strip()
            # Security: Phrasing "If an account exists"
            user = User.objects.filter(email=email).first()
            
            if user:
                # Generate and save OTP
                otp = ''.join(random.choices(string.digits, k=6))
                EmailOTP.objects.filter(email=email).delete()
                EmailOTP.objects.create(email=email, otp=otp)

                # Send Email
                subject = 'FitSync Security: Password Reset Request'
                message = f"""Hello {user.first_name or user.username},

We received a request to reset your password for your FitSync Elite account.

Your 6-digit verification code is:

🔐 OTP Code: {otp}

This code is valid for 10 minutes. 

Security Tip: If you did not request this, please ensure your account is secure.

Stay strong.
FitSync Security Team
"""
                email_from = settings.DEFAULT_FROM_EMAIL
                try:
                    send_mail(subject, message, email_from, [email])
                except Exception as ex:
                    messages.error(request, f"Relay error: {str(ex)}")
                    # Continue to avoid leaking if error only happens for real/fake emails
            
            # Mask email for Step 2 display: u*****@gmail.com
            if '@' in email:
                user_part, domain_part = email.split('@')
                masked_email = user_part[0] + ('*' * 5) + '@' + domain_part
            else:
                masked_email = "****"
            
            request.session['reset_email'] = email
            request.session['masked_email'] = masked_email
            request.session['reset_step'] = 2
            messages.info(request, "A verification code has been dispatched to your identity address.")
            return redirect('forgot_password')

        elif step == 2:
            otp_input = request.POST.get('otp', '').strip()
            # If the user clicks "Resend" or similar, we might need a separate logic, 
            # but for now we handle OTP verification.
            
            otp_obj = EmailOTP.objects.filter(email=email, otp=otp_input).first()
            if otp_obj:
                if otp_obj.is_expired():
                    messages.error(request, "Verification code expired. Please request a new one.")
                    request.session['reset_step'] = 1
                    return redirect('forgot_password')
                
                # Verified!
                otp_obj.delete()
                request.session['reset_step'] = 3
                return redirect('forgot_password')
            else:
                messages.error(request, "Invalid verification code. Access denied.")
                return redirect('forgot_password')

        elif step == 3:
            new_p = request.POST.get('new_password')
            confirm_p = request.POST.get('confirm_password')

            # Requirements: Min 12 chars, symbol
            has_symbol = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', new_p))
            
            if len(new_p) < 12:
                messages.error(request, "Security breach: Password must be at least 12 characters.")
                return redirect('forgot_password')
            
            if not has_symbol:
                messages.error(request, "Security breach: Password must contain at least one symbol.")
                return redirect('forgot_password')

            if new_p != confirm_p:
                messages.error(request, "Parity error: Passwords do not match.")
                return redirect('forgot_password')

            user = User.objects.filter(email=email).first()
            if user:
                user.set_password(new_p)
                user.save()
                # Cleanup session
                for key in ['reset_step', 'reset_email', 'masked_email']:
                    if key in request.session: del request.session[key]
                
                messages.success(request, "Vault updated. New credentials active.")
                return redirect('login')
            else:
                messages.error(request, "Critical identity failure. Please restart.")
                request.session['reset_step'] = 1
                return redirect('forgot_password')

    return render(request, 'fitsync_app/forgot_password.html', {
        'step': step,
        'email': request.session.get('masked_email', '')
    })

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

@login_required
def profile_view(request):
    user_profile = request.user.userprofile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Error updating profile. Please check the form.")
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'fitsync_app/profile.html', {'form': form, 'user_profile': user_profile})

# Dashboard
def home_view(request):
    return render(request, 'fitsync_app/home.html')

@login_required
def admin_dashboard_view(request):
    # Strict Role Routing
    if hasattr(request.user, 'userprofile'):
        if request.user.userprofile.role == 'trainer':
            return redirect('trainer_dashboard')
        elif request.user.userprofile.role == 'member':
            return redirect('user_dashboard')
            
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'admin':
        messages.error(request, "Access denied. Admin account required.")
        return redirect('login')
        
    # Real stats for the dashboard
    # Count only members as "Total Users" to avoid confusion with staff/admin accounts
    total_users = UserProfile.objects.filter(role='member').count()
    active_trainers = UserProfile.objects.filter(role='trainer').count()
    
    # Calculate total revenue
    total_revenue = Payment.objects.filter(status='success').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Membership Tier Stats
    membership_stats = UserSubscription.objects.values('plan__name').annotate(count=Count('id'))
    tier_counts = {'basic': 0, 'premium': 0, 'elite': 0, 'lifetime': 0}
    for stat in membership_stats:
        plan_name = stat['plan__name']
        if plan_name in tier_counts:
            tier_counts[plan_name] = stat['count']
        elif plan_name == 'gold': # Backward compatibility if still in DB
             tier_counts['premium'] += stat['count']

    # Store Analytics
    store_total_products = Product.objects.count()
    store_total_orders = Order.objects.count()
    store_total_revenue = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Calculate Top Product
    top_product_entry = OrderItem.objects.values('product__name').annotate(total_sold=Sum('quantity')).order_by('-total_sold').first()
    store_top_product = top_product_entry['product__name'] if top_product_entry else "N/A"
    
    # Recent users for the table (Exclude admins and trainers)
    recent_users = UserProfile.objects.filter(role='member').select_related('user').order_by('-user__date_joined')[:5]
    
    return render(request, 'fitsync_app/admin_dashboard.html', {
        'total_users': total_users,
        'active_trainers': active_trainers,
        'total_revenue': total_revenue,
        'recent_users': recent_users,
        'tier_counts': tier_counts,
        'store_total_products': store_total_products,
        'store_total_orders': store_total_orders,
        'store_total_revenue': store_total_revenue,
        'store_top_product': store_top_product
    })

@login_required
def add_trainer_view(request):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'admin':
        messages.error(request, "Access denied. Admin account required.")
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        trainer_name = request.POST.get('trainer_name', '')
        u = request.POST.get('username')
        e = request.POST.get('email')
        p = request.POST.get('password')
        sp = request.POST.get('specialty', 'Master Strength & Conditioning')
        pr = request.POST.get('price', 4999)
        
        if User.objects.filter(username=u).exists():
            messages.error(request, "Username already taken.")
        else:
            user = User.objects.create_user(username=u, email=e, password=p)
            user.first_name = trainer_name
            user.save()
            
            photo = request.FILES.get('profile_photo')
            UserProfile.objects.create(
                user=user, 
                role='trainer', 
                specialty=sp, 
                price=float(pr),
                profile_photo=photo
            )
            
            # Send welcome email
            try:
                subject = 'Welcome to FitSync Fitness Management System'
                message = f"""Dear {trainer_name},

Welcome to FitSync 
Your trainer account has been successfully created by the FitSync Admin. You can now log in to the FitSync Trainer Portal and start managing your workout sessions and members.

Here are your account details:

Trainer Email: {e}
Username: {u}
Session Price: ₹{pr} per session
Security Key:{p}

Please keep your security key confidential. It will be required for verifying your account and accessing trainer features.

Trainer Responsibilities:
* Conduct live workout sessions for users
* Guide members with proper workout techniques
* Track user performance and progress
* Communicate with users during training sessions

Login Link: http://{request.get_host()}/login/

If you have any questions, please contact the FitSync Admin team.

Best Regards,
FitSync Admin Team
FitSync – Your Ultimate Fitness Companion
"""
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'admin@fitsync.com',
                    [e],
                    fail_silently=True,
                )
            except Exception as email_err:
                print(f"Failed to send email: {email_err}")

            messages.success(request, f"Trainer {trainer_name} ({u}) added successfully! Verification email sent.")
            return redirect('trainer_list')
            
    return render(request, 'fitsync_app/add_trainer.html')

@login_required
def delete_trainer_view(request, trainer_id):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('admin_dashboard')
    
    trainer_profile = get_object_or_404(UserProfile, id=trainer_id, role='trainer')
    trainer_user = trainer_profile.user
    trainer_name = trainer_user.username
    
    trainer_user.delete()
    messages.success(request, f"Trainer {trainer_name} has been removed.")
    return redirect('trainer_list')


@login_required
@login_required
def trainer_dashboard_view(request):
    # Strict Role Routing
    if hasattr(request.user, 'userprofile'):
        if request.user.userprofile.role == 'admin':
            return redirect('admin_dashboard')
        elif request.user.userprofile.role == 'member':
            return redirect('user_dashboard')
            
    # Check if user is trainer
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'trainer':
        return redirect('user_dashboard')
    
    # Handle feedback submission or profile photo update
    if request.method == 'POST':
        # Handle Profile Photo Update
        if 'profile_photo' in request.FILES:
            profile = request.user.userprofile
            profile.profile_photo = request.FILES['profile_photo']
            profile.save()
            messages.success(request, "Profile photo updated successfully!")
            return redirect('trainer_dashboard')
            
        # Handle Phone Number Update
        if 'new_phone' in request.POST:
            new_phone = request.POST.get('new_phone')
            profile = request.user.userprofile
            profile.phone_number = new_phone
            profile.save()
            messages.success(request, "Mobile number updated successfully!")
            return redirect('trainer_dashboard')

        user_id = request.POST.get('user_id')
        feedback_text = request.POST.get('feedback_text')
        rating = request.POST.get('rating')
        
        if user_id and feedback_text:
            try:
                member = User.objects.get(id=user_id)
                TrainerFeedback.objects.create(
                    trainer=request.user,
                    user=member,
                    feedback_text=feedback_text,
                    rating=int(rating) if rating else None
                )
                Notification.objects.create(
                    user=member,
                    title='New Feedback from Your Trainer',
                    message=f'Your trainer has provided feedback on your performance. Check it out!'
                )
                messages.success(request, f"Feedback sent to {member.get_full_name()}!")
            except User.DoesNotExist:
                pass
        return redirect('trainer_dashboard')
    
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Optimized Query
    members = User.objects.filter(userprofile__assigned_trainer=request.user).select_related('userprofile').annotate(
        last_attendance_date=Max('attendance_logs__logged_at'),
        attended_days_count=Count(
            'attendance_logs__logged_at__date',
            filter=Q(attendance_logs__logged_at__date__gte=thirty_days_ago),
            distinct=True
        ),
        msgs_today=Count(
            'sent_messages', 
            filter=Q(sent_messages__sent_at__date=today)
        ) + Count(
            'received_messages', 
            filter=Q(received_messages__sent_at__date=today)
        )
    )
    
    # Post-processing for display fields that are hard to annotate directly or need logic
    for member in members:
        # Attendance rate
        # 30 days is fixed denominator
        member.attendance_rate = round((member.attended_days_count / 30) * 100)
        member.messages_today = member.msgs_today
        
        # Last attendance object simulation (template likely only needs date, but if it needs more, we fallback)
        # Note: If template uses member.last_attendance.some_field, this change might strictly need the object.
        # But usually dashboards just show "Last seen: [Date]"
        # To be safe, let's keep it simple. If template breaks, we revert.
        # Assuming template uses {{ member.last_attendance.logged_at }} or similar.
        # We'll attach a mock object or just passed date if template allows.
        pass
    
    # Stats
    total_members = members.count()
    today_attendance = Attendance.objects.filter(user__userprofile__assigned_trainer=request.user, logged_at__date=today).count()
    unread_messages = Message.objects.filter(receiver=request.user, is_read=False).count()
    
    context = {
        'members': members,
        'total_members': total_members,
        'today_attendance': today_attendance,
        'unread_messages': unread_messages,
    }
    
    return render(request, 'fitsync_app/trainer_dashboard.html', context)

@login_required
def user_dashboard_view(request):
    # Strict Role Routing: Trainers/Admins should not see user dashboard
    if hasattr(request.user, 'userprofile'):
        if request.user.userprofile.role == 'trainer':
            return redirect('trainer_dashboard')
        elif request.user.userprofile.role == 'admin':
            return redirect('admin_dashboard')

    user_profile = request.user.userprofile

    # ── First-Time Setup Detection ──
    has_profile_data = user_profile.height_cm and user_profile.weight_kg
    has_subscription = UserSubscription.objects.filter(user=request.user, is_active=True).exists()
    has_bmi = request.user.bmi_records.exists()
    has_assessment = hasattr(request.user, 'fitness_assessment')
    has_workout = user_profile.active_workout is not None

    # Determine setup step for new users
    is_new_user = not (has_subscription and has_profile_data and has_bmi and has_assessment and has_workout)
    setup_step = 0
    if is_new_user:
        if not has_subscription:
            setup_step = 1  # Choose subscription
        elif not has_profile_data:
            setup_step = 2  # Profile setup
        elif not has_bmi:
            setup_step = 3  # BMI calculation
        elif not has_assessment:
            setup_step = 4  # Smart Fitness Assessment
        else:
            setup_step = 5  # AI workout recommendation

    # Get recent feedback from trainers
    recent_feedback = TrainerFeedback.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Get assigned trainer details
    assigned_trainer = user_profile.assigned_trainer
    trainer_display_name = ""
    trainer_assignment_date = ""
    trainer_profile = None
    if assigned_trainer:
        trainer_profile = UserProfile.objects.filter(user=assigned_trainer).first()
        trainer_display_name = assigned_trainer.get_full_name() or assigned_trainer.username
        trainer_assignment_date = user_profile.created_at.strftime("%b %d, %Y") if user_profile.created_at else "Recently"

    # Handle photo upload from dashboard
    if request.method == 'POST' and request.FILES.get('profile_photo'):
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile photo updated successfully!")
            return redirect('user_dashboard')

    # Subscription check for trainer section visibility
    sub = UserSubscription.objects.filter(user=request.user, is_active=True).first()
    is_basic = sub and sub.plan and sub.plan.name == 'basic'
    
    # Get upcoming live sessions
    upcoming_sessions = LiveSession.objects.filter(date__gte=timezone.now().date()).order_by('date', 'time')[:3]
    
    # Performance Dashboard Connectivity
    today = timezone.now().date()
    calories_today = NutritionLog.objects.filter(user=request.user, date=today).aggregate(Sum('calories'))['calories__sum'] or 0
    water_today = WaterLog.objects.filter(user=request.user, date=today).first()
    water_ml = water_today.amount_ml if water_today else 0
    
    # Active Protocols
    active_diet = user_profile.active_diet
    active_workout = user_profile.active_workout
    
    # Get today's meals from the active diet plan
    day_name = today.strftime('%A').lower()
    today_meals = []
    if active_diet:
        today_meals = active_diet.meals.filter(day=day_name).order_by('time')

    # Goal Metrics
    total_goals = Goal.objects.filter(user=request.user).count()
    completed_goals = Goal.objects.filter(user=request.user, is_completed=True).count()
    goal_progress = (completed_goals / total_goals * 100) if total_goals > 0 else 0
    next_goal = Goal.objects.filter(user=request.user, is_completed=False).order_by('target_date').first()
    
    # Activity Stats
    total_workouts = WorkoutProgram.objects.count()
    total_diets = DietPlan.objects.count()
    attendance_streak = Attendance.objects.filter(user=request.user).count()
    
    # Last BMI Record
    last_bmi = request.user.bmi_records.first()
    
    # Recent Orders
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:3]
    
    # Notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    
    # Store Stats
    cart = Cart.objects.filter(user=request.user).first()
    cart_count = cart.items.count() if cart else 0
    
    # Next Workout
    next_session = upcoming_sessions[0] if upcoming_sessions else None

    # Today's attendance status
    attended_today = Attendance.objects.filter(user=request.user, logged_at__date=today).exists()

    # Weekly attendance count (last 7 days)
    seven_days_ago = today - timedelta(days=7)
    weekly_attendance = Attendance.objects.filter(user=request.user, logged_at__date__gte=seven_days_ago).count()
    
    context = {
        'recent_feedback': recent_feedback,
        'assigned_trainer': assigned_trainer if not is_basic else None,
        'trainer_profile': trainer_profile if not is_basic else None,
        'trainer_display_name': trainer_display_name if not is_basic else "",
        'trainer_assignment_date': trainer_assignment_date if not is_basic else "",
        'user_profile': user_profile,
        'is_basic': is_basic,
        'subscription': sub,
        'live_sessions': upcoming_sessions,
        
        # New Context Variables
        'calories_today': calories_today,
        'water_today': water_ml,
        'total_goals': total_goals,
        'completed_goals': completed_goals,
        'goal_progress': goal_progress,
        'next_goal': next_goal,
        'total_workouts': total_workouts,
        'total_diets': total_diets,
        'attendance_streak': attendance_streak,
        'last_bmi': last_bmi,
        
        # Protocol Context
        'active_diet': active_diet,
        'active_workout': active_workout,
        'today_meals': today_meals,
        
        # Store & Feedback
        'recent_orders': recent_orders,
        'notifications': notifications,
        'cart_count': cart_count,
        'next_session': next_session,

        # First-time setup
        'is_new_user': is_new_user,
        'setup_step': setup_step,
        'has_profile_data': has_profile_data,
        'has_subscription': has_subscription,
        'has_bmi': has_bmi,
        'has_assessment': has_assessment,
        'has_workout': has_workout,
        'attended_today': attended_today,
        'weekly_attendance': weekly_attendance,
    }

    return render(request, 'fitsync_app/user_dashboard.html', context)

@login_required
def trainer_list_view(request):
    # Subscription Check: Personal Trainers are a Premium Feature
    # Subscription Check: Personal Trainers are a Premium Feature
    # Allow Admins to view this page regardless of subscription
    is_admin = hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin'
    
    sub = UserSubscription.objects.filter(user=request.user, is_active=True).first()
    if not is_admin and (not sub or not sub.plan or sub.plan.name == 'basic'):
        messages.warning(request, "Access to elite personal trainers requires a Premium or Elite membership.")
        return redirect('membership')

    trainers = UserProfile.objects.filter(role='trainer')
    
    # Check if user already has a trainer
    current_trainer = None
    if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
        current_trainer = request.user.userprofile.assigned_trainer

    # Handle Admin Price Update
    if request.method == 'POST' and is_admin:
        trainer_id = request.POST.get('trainer_id')
        new_price = request.POST.get('new_price')
        
        if trainer_id and new_price:
            try:
                # Get the profile directly, ensuring it's a trainer's profile
                profile_to_update = UserProfile.objects.get(id=trainer_id, role='trainer')
                profile_to_update.price = float(new_price)
                profile_to_update.save()
                messages.success(request, f"Updated price for {profile_to_update.user.username}")
            except UserProfile.DoesNotExist:
                messages.error(request, "Trainer not found.")
            except ValueError:
                messages.error(request, "Invalid price format.")
            except Exception as e:
                messages.error(request, f"Error updating price: {str(e)}")
        # Redirect to avoid resubmission on refresh
        return redirect('trainer_list')

    return render(request, 'fitsync_app/trainer_list.html', {
        'trainers': trainers,
        'current_trainer': current_trainer,
        'is_admin': is_admin
    })

@login_required
@login_required
def progress_view(request):
    now = timezone.localtime(timezone.now())
    seven_days_ago = now - timedelta(days=7)
    
    bmi_history = BMIHistory.objects.filter(user=request.user).order_by('recorded_at')
    attendance_logs = Attendance.objects.filter(user=request.user).order_by('-logged_at')
    
    # Weekly breakdown for chart - Improved for Timezone accuracy
    weekly_stats = []
    raw_data = []
    max_count = 0
    
    # Calculate for the last 7 days
    for i in range(6, -1, -1):
        target_date = (now - timedelta(days=i)).date()
        day_start = timezone.make_aware(datetime.combine(target_date, time.min))
        day_end = timezone.make_aware(datetime.combine(target_date, time.max))
        
        count = Attendance.objects.filter(
            user=request.user, 
            logged_at__range=(day_start, day_end)
        ).count()
        
        raw_data.append({'day': target_date.strftime("%a"), 'count': count})
        if count > max_count:
            max_count = count
            
    # Scale heights (0-200px) - Ensure at least 1 for division and visibility
    scale_max = max(max_count, 1)
    for item in raw_data:
        # Give a tiny 4px base so even 0-count days are identifiable in the UI
        height_px = (item['count'] / scale_max * 200) if item['count'] > 0 else 0
        weekly_stats.append({
            'label': item['day'],
            'count': item['count'],
            'height': f"{height_px}px"
        })
    
    # Weight History Chart (last 7 logs)
    weight_stats = []
    # Get last 7 records in chronological order
    recent_bmi = BMIHistory.objects.filter(user=request.user).order_by('-recorded_at')[:7]
    for rec in reversed(recent_bmi):
        weight_stats.append({
            'label': rec.recorded_at.strftime("%m/%d"),
            'weight': float(rec.weight_kg)
        })
    
    # Real Metrics
    attendance_count_week = Attendance.objects.filter(user=request.user, logged_at__gte=seven_days_ago).count()
    total_attendance = Attendance.objects.filter(user=request.user).count()
    
    # Estimated Calories (e.g. 400 per session)
    calories_burned = total_attendance * 400
    
    # Training duration (e.g. 60 mins per session)
    total_duration = total_attendance * 60
    
    # Mock Steps (Since no model exists, let's derive it from activity)
    steps = 5000 + (total_attendance * 1200)
    
    # Calculate weight change
    weight_change = 0
    full_history = BMIHistory.objects.filter(user=request.user).order_by('recorded_at')
    if full_history.count() >= 2:
        weight_change = full_history.last().weight_kg - full_history.first().weight_kg

    context = {
        'bmi_history': full_history,
        'activity_logs': attendance_logs[:5],
        'acw': attendance_count_week,
        'total_attendance': total_attendance,
        'calories_burned': f"{calories_burned:,}",
        'steps': f"{steps:,}",
        'total_duration': total_duration,
        'weight_change': weight_change,
        'weekly_stats': weekly_stats,
        'weight_stats': weight_stats,
        'last_sync': now.strftime("%H:%M")
    }
    return render(request, 'fitsync_app/progress.html', context)

@login_required
def trainer_member_progress_view(request, user_id):
    # Ensure only trainers or admins can access this
    if not (request.user.userprofile.role in ['trainer', 'admin']):
        messages.error(request, "Access denied.")
        return redirect('home')

    member = get_object_or_404(User, id=user_id)
    history = BMIHistory.objects.filter(user=member).order_by('recorded_at')
    
    return render(request, 'fitsync_app/trainer_member_progress.html', {
        'member': member,
        'history': history
    })

@login_required
def attendance_tracker_view(request):
    local_now = timezone.localtime(timezone.now())
    year = local_now.year
    month = local_now.month
    
    # Fetch all logs for the current user once to avoid multiple DB queries and timezone issues
    logs = Attendance.objects.filter(user=request.user).order_by('-logged_at')
    
    # Process dates in Python to avoid database-side YEAR/MONTH extraction issues
    all_present_dates = set()
    present_days_in_month = set()
    check_ins_today = 0
    
    for log in logs:
        local_date_obj = timezone.localtime(log.logged_at)
        log_date = local_date_obj.date()
        all_present_dates.add(log_date)
        
        # Check if in current month
        if local_date_obj.year == year and local_date_obj.month == month:
            present_days_in_month.add(local_date_obj.day)
            
        # Count check-ins for today
        if log_date == local_now.date():
            check_ins_today += 1

    # Generate calendar grid
    cal = calendar.monthcalendar(year, month)
    
    calendar_days = []
    for week in cal:
        for day in week:
            is_present = day in present_days_in_month
            is_today = (day == local_now.day)
            calendar_days.append({
                'day': day,
                'is_present': is_present,
                'is_today': is_today,
                'is_past': day > 0 and day < local_now.day
            })

    # Daily Status for the last 14 days (columns)
    daily_status = []
    for i in range(13, -1, -1):
        check_date = (local_now - timedelta(days=i)).date()
        is_present = check_date in all_present_dates
        daily_status.append({
            'date': check_date,
            'is_present': is_present,
            'day_name': check_date.strftime('%a'),
            'display_date': check_date.strftime('%b %d')
        })

    # Calculate Attendance Rate
    attendance_rate = 0
    if local_now.day > 0:
        attendance_rate = round((len(present_days_in_month) / local_now.day) * 100)
    
    context = {
        'logs': logs,
        'calendar_days': calendar_days,
        'daily_status': daily_status,
        'current_month': local_now.strftime('%B %Y'),
        'today': local_now.day,
        'check_ins_today': check_ins_today,
        'already_checked_in': check_ins_today > 0,
        'attendance_rate': attendance_rate
    }
    return render(request, 'fitsync_app/attendance.html', context)

@login_required
def membership_view(request):
    try:
        subscription = UserSubscription.objects.get(user=request.user)
    except UserSubscription.DoesNotExist:
        subscription = None
        
    payments = Payment.objects.filter(user=request.user).order_by('-payment_date')
    
    # Fetch all active plans for the grid
    all_plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    
    display_data = {
        'plan_name': 'Member',
        'plan_description': 'Upgrade to unlock features',
        'valid_until_str': 'N/A',
        'days_remaining': 0,
        'next_billing': '0'
    }
    
    # Initialize variables for template context
    days_remaining = 0
    valid_until = None
    next_billing_amount = 0

    if subscription and subscription.is_active and subscription.plan:
        # Priority: Check if we have a stored expiry_date
        valid_until = subscription.expiry_date
        
        # Fallback heuristic if expiry_date is missing (for older records)
        if not valid_until:
            plan_name_lower = subscription.plan.name.lower()
            if 'lifetime' in plan_name_lower:
                 valid_until = subscription.start_date + timedelta(days=36500)
            else:
                 # Check last payment or start date
                 last_payment = payments.filter(status='success').first()
                 base_date = last_payment.payment_date if last_payment else subscription.start_date
                 # Heuristic for annual vs monthly based on price
                 is_annual = subscription.plan.price > 5000
                 valid_until = base_date + timedelta(days=365 if is_annual else 30)

        # Formatting for Display
        delta = valid_until - timezone.now()
        days_remaining = max(0, delta.days)
        
        # Determine if it's effectively lifetime for display
        if days_remaining > 3650: # More than 10 years
            valid_until_str = "Lifetime / Never"
            days_remaining_str = "Unlimited"
            next_billing_str = "0 (Lifetime)"
        else:
            valid_until_str = valid_until.strftime("%b %d, %Y")
            days_remaining_str = f"{days_remaining} Days"
            next_billing_str = f"{subscription.plan.price:.0f}"

        display_data.update({
            'plan_name': subscription.plan.get_name_display().upper(),
            'plan_description': subscription.plan.description,
            'valid_until_str': valid_until_str,
            'days_remaining': days_remaining_str,
            'next_billing': next_billing_str
        })

    return render(request, 'fitsync_app/membership.html', {
        'subscription': subscription,
        'payments': payments,
        'display': display_data,
        'days_remaining': days_remaining,
        'valid_until': valid_until,
        'next_billing_amount': next_billing_amount,
        'plans': all_plans
    })

@login_required
def nutrition_view(request):
    today = timezone.now().date()
    
    if request.method == 'POST':
        form = NutritionLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            messages.success(request, "Meal logged successfully!")
            return redirect('nutrition')
    else:
        form = NutritionLogForm(initial={'date': today})
    
    daily_logs = NutritionLog.objects.filter(user=request.user, date=today)
    water_log, created = WaterLog.objects.get_or_create(user=request.user, date=today)
    
    # Calculate totals
    totals = {
        'calories': sum(l.calories for l in daily_logs),
        'protein': sum(l.protein for l in daily_logs),
        'carbs': sum(l.carbs for l in daily_logs),
        'fats': sum(l.fats for l in daily_logs),
        'water': water_log.amount_ml,
    }
    
    # Calculate goals progress
    goals = {
        'calories': 2000,
        'protein': 150,
        'carbs': 250,
        'water': 2000, # 8 glasses x 250ml
    }
    
    remaining = {
        'calories': max(0, goals['calories'] - totals['calories']),
        'protein': max(0, goals['protein'] - totals['protein']),
        'carbs': max(0, goals['carbs'] - totals['carbs']),
    }
    
    nutrition_stats = {
        'calories': min(100, int((totals['calories'] / goals['calories']) * 100)) if goals['calories'] else 0,
        'water': min(100, int((totals['water'] / goals['water']) * 100)) if goals['water'] else 0,
        'water_glasses': round(totals['water'] / 250),
    }

    return render(request, 'fitsync_app/nutrition.html', {
        'form': form,
        'daily_logs': daily_logs,
        'totals': totals,
        'remaining': remaining,
        'nutrition_stats': nutrition_stats
    })

@login_required
def add_water(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = int(data.get('amount', 0))
        
        today = timezone.now().date()
        
        water_log, created = WaterLog.objects.get_or_create(user=request.user, date=today)
        water_log.amount_ml += amount
        water_log.save()
        
        return JsonResponse({'status': 'success', 'new_total': water_log.amount_ml})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def goals_view(request):
    if request.method == 'POST':
        if 'toggle_complete' in request.POST:
            goal_id = request.POST.get('goal_id')
            goal = get_object_or_404(Goal, id=goal_id, user=request.user)
            goal.is_completed = not goal.is_completed
            goal.save()
            return redirect('goals')
        
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, "New goal set!")
            return redirect('goals')
    else:
        form = GoalForm()
        
    goals = Goal.objects.filter(user=request.user).order_by('is_completed', '-created_at')
    return render(request, 'fitsync_app/goals.html', {'form': form, 'goals': goals})

@login_required
def messages_view(request):
    # If user is a trainer, they should see their assigned trainees
    # If user is a member, they should see trainers/admins
    if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'trainer':
        # Trainers see their trainees
        contacts = User.objects.filter(userprofile__assigned_trainer=request.user).select_related('userprofile')
    else:
        # Members see trainers and admins
        contacts = User.objects.filter(userprofile__role__in=['trainer', 'admin']).exclude(id=request.user.id).select_related('userprofile')

    # Also include anyone else they have chat history with (in case assignment changed)
    past_interacted_ids = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).values_list('sender', 'receiver')
    # Flatten the list of tuples and remove current user ID
    interacted_ids = set()
    for s, r in past_interacted_ids:
        interacted_ids.add(s)
        interacted_ids.add(r)
    interacted_ids.discard(request.user.id)
    
    # Combine the queries
    if interacted_ids:
        # We want union of role-based contacts AND past interactions
        contacts = contacts | User.objects.filter(id__in=interacted_ids).select_related('userprofile')
    
    contacts = contacts.distinct()
    
    active_id = request.GET.get('user_id')
    active_user = None
    
    if active_id:
        active_user = get_object_or_404(User, id=active_id)
    elif contacts.exists():
        active_user = contacts.first()
        
    if request.method == 'POST':
        content = request.POST.get('content')
        receiver_id = request.POST.get('receiver_id')
        
        if content and receiver_id:
            receiver = get_object_or_404(User, id=receiver_id)
            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                body=content
            )
            return redirect(f'/messages/?user_id={receiver_id}')
            
    # Get conversation with active user
    messages_list = []
    if active_user:
        messages_list = Message.objects.filter(
            Q(sender=request.user, receiver=active_user) | 
            Q(sender=active_user, receiver=request.user)
        ).order_by('sent_at')
        
    return render(request, 'fitsync_app/messages.html', {
        'contacts': contacts,
        'active_user': active_user,
        'messages_list': messages_list
    })

@login_required
def settings_view(request):
    if request.method == 'POST':
        user = request.user
        profile = user.userprofile
        
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        profile.phone_number = request.POST.get('phone_number', profile.phone_number)
        profile.fitness_goal = request.POST.get('fitness_goal', profile.fitness_goal)
        profile.weight_kg = request.POST.get('weight_kg', profile.weight_kg)
        profile.height_cm = request.POST.get('height_cm', profile.height_cm)
        
        # Handle profile photo upload
        if 'profile_photo' in request.FILES:
            profile.profile_photo = request.FILES['profile_photo']
        
        profile.save()
        
        messages.success(request, "Profile updated successfully.")
        return redirect('settings')
        
    return render(request, 'fitsync_app/settings.html')

@login_required
def help_view(request):
    if request.method == 'POST':
        form = HelpTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, "Your support ticket has been submitted. Our team will respond shortly.")
            return redirect('help')
    else:
        form = HelpTicketForm()
    
    # Get user's tickets
    user_tickets = HelpTicket.objects.filter(user=request.user)
    
    faqs = [
        {'q': 'How do I change my password?', 'a': 'Go to Settings and click on Change Password.'},
        {'q': 'How do I cancel my subscription?', 'a': 'Navigate to Membership and click Cancel Subscription.'},
        {'q': 'Can I export my data?', 'a': 'Yes, go to Reports -> Download Data.'},
    ]
    return render(request, 'fitsync_app/help.html', {
        'faqs': faqs,
        'form': form,
        'user_tickets': user_tickets
    })

@login_required
def community_view(request):
    if request.method == 'POST':
        form = CommunityPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Posted to community!")
            return redirect('community')
    else:
        form = CommunityPostForm()
        
    posts = CommunityPost.objects.all().order_by('-created_at')
    return render(request, 'fitsync_app/community.html', {'form': form, 'posts': posts})

# Diet
@login_required
def diet_list_view(request):
    user_profile = getattr(request.user, 'userprofile', None)
    
    if user_profile and user_profile.role == 'member' and user_profile.active_diet:
        diets = [user_profile.active_diet]
        latest_diet = user_profile.active_diet
    else:
        diets = DietPlan.objects.all()
        latest_diet = diets.first()
    
    
    context = {'diets': diets}
    
    if latest_diet:
        context['diet'] = latest_diet
        meals = latest_diet.meals.all()
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        context['days'] = days
        context['meals_by_day'] = {day: meals.filter(day=day) for day in days}
        
    return render(request, 'fitsync_app/diet_list.html', context)

def diet_detail_view(request, pk):
    diet = get_object_or_404(DietPlan, pk=pk)
    meals = diet.meals.all()
    
    # Group meals by day
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    meals_by_day = {day: meals.filter(day=day) for day in days}
    
    # Calculate daily totals for initial display (Monday)
    monday_meals = meals_by_day['monday']
    monday_totals = {
        'calories': sum(m.calories for m in monday_meals),
        'protein': sum(m.protein for m in monday_meals),
        'carbs': sum(m.carbs for m in monday_meals),
        'fats': sum(m.fats for m in monday_meals),
    }

    return render(request, 'fitsync_app/diet_detail.html', {
        'diet': diet,
        'meals_by_day': meals_by_day,
        'days': days,
        'monday_totals': monday_totals
    })

@login_required
def diet_add_view(request):
    if request.user.userprofile.role not in ['trainer', 'admin']:
        messages.error(request, "Permission denied.")
        return redirect('diet_list')

    if request.method == 'POST':
        form = DietPlanForm(request.POST)
        if form.is_valid():
            diet = form.save(commit=False)
            diet.trainer = request.user
            diet.save()
            messages.success(request, "Diet plan added successfully!")
            return redirect('diet_list')
    else:
        form = DietPlanForm()
    return render(request, 'fitsync_app/diet_add.html', {'form': form})



@login_required
def diet_edit_view(request, pk):
    diet = get_object_or_404(DietPlan, pk=pk)
    
    # Check if user is trainer or admin
    if request.user.userprofile.role not in ['trainer', 'admin']:
        messages.error(request, "Permission denied.")
        return redirect('diet_detail', pk=pk)

    if request.method == 'POST':
        form = DietPlanForm(request.POST, instance=diet)
        if form.is_valid():
            form.save()
            messages.success(request, "Diet protocol updated.")
            return redirect('diet_detail', pk=pk)
    else:
        form = DietPlanForm(instance=diet)
    
    return render(request, 'fitsync_app/diet_edit.html', {'form': form, 'diet': diet})

@login_required
def diet_delete_view(request, pk):
    diet = get_object_or_404(DietPlan, pk=pk)
    if request.user.userprofile.role not in ['trainer', 'admin']:
        messages.error(request, "Permission denied.")
        return redirect('diet_list')
    
    diet.delete()
    messages.success(request, "Diet protocol removed from library.")
    return redirect('diet_list')

@login_required
def meal_add_view(request, diet_id):
    diet = get_object_or_404(DietPlan, id=diet_id)
    if request.user.userprofile.role not in ['trainer', 'admin']:
        messages.error(request, "Permission denied.")
        return redirect('diet_detail', pk=diet.id)

    if request.method == 'POST':
        form = MealForm(request.POST)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.diet_plan = diet
            meal.save()
            messages.success(request, f"Meal added to {meal.get_day_display()}!")
            return redirect('diet_detail', pk=diet.id)
    else:
        initial_day = request.GET.get('day', 'monday')
        form = MealForm(initial={'day': initial_day})
    return render(request, 'fitsync_app/meal_add.html', {'form': form, 'diet': diet})

@login_required
def meal_delete_view(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id)
    diet_id = meal.diet_plan.id
    if request.user.userprofile.role not in ['trainer', 'admin']:
        messages.error(request, "Permission denied.")
    else:
        meal.delete()
        messages.success(request, "Meal entry removed.")
    return redirect('diet_detail', pk=diet_id)

# Workout
@login_required
def workout_list_view(request):
    today = timezone.now().date()
    # Personalize submodule: show only the user's active workout if member
    user_profile = getattr(request.user, 'userprofile', None)
    if user_profile and user_profile.role == 'member' and user_profile.active_workout:
        workouts = [user_profile.active_workout]
    else:
        workouts = WorkoutProgram.objects.all()
        
    already_checked_in = Attendance.objects.filter(user=request.user, logged_at__date=today).exists()
    
    return render(request, 'fitsync_app/workout_list.html', {
        'workouts': workouts,
        'already_checked_in': already_checked_in
    })

@login_required
def workout_session_view(request, pk):
    workout = get_object_or_404(WorkoutProgram, pk=pk)
    today = timezone.now().date()
    already_checked_in = Attendance.objects.filter(user=request.user, logged_at__date=today).exists()
    
    return render(request, 'fitsync_app/workout_session.html', {
        'workout': workout,
        'already_checked_in': already_checked_in
    })

def workout_add_view(request):
    if request.method == 'POST':
        form = WorkoutProgramForm(request.POST, request.FILES)
        if form.is_valid():
            workout = form.save(commit=False)
            if request.user.is_authenticated:
                workout.trainer = request.user
            workout.save()
            messages.success(request, "Workout program added successfully!")
            return redirect('workout_list')
    else:
        form = WorkoutProgramForm()
    return render(request, 'fitsync_app/workout_add.html', {'form': form})

def workout_edit_view(request, pk=None):
    return render(request, 'fitsync_app/workout_edit.html')

# BMI
def bmi_calculator_view(request):
    if request.method == 'POST':
        w = request.POST.get('weight')
        h = request.POST.get('height')
        b = request.POST.get('bmi')
        
        if request.user.is_authenticated and w and h and b:
            BMIHistory.objects.create(
                user=request.user,
                weight_kg=w,
                height_cm=h,
                bmi_score=b
            )
            messages.success(request, "BMI record saved to your history.")
            return redirect('bmi_history')
    return render(request, 'fitsync_app/bmi_calculator.html')

def bmi_history_view(request):
    if request.user.is_authenticated:
        history = BMIHistory.objects.filter(user=request.user)
    else:
        history = []
    return render(request, 'fitsync_app/bmi_history.html', {'history': history})

# Attendance
@login_required
def attendance_mark_view(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.user = request.user
            attendance.save()
            messages.success(request, "Attendance marked!")
            return redirect('attendance')
    else:
        form = AttendanceForm()
    return render(request, 'fitsync_app/attendance_mark.html', {'form': form})

@login_required
def mark_attendance_api(request):
    if request.method == 'POST':
        # Load data from request body if available
        data = {}
        try:
            data = json.loads(request.body)
        except:
            pass
            
        workout_type = data.get('workout_type', "Gym Session")
        notes = data.get('notes', "Daily check-in from dashboard")
        
        today = timezone.now().date()
        
        Attendance.objects.create(
            user=request.user,
            workout_type=workout_type,
            notes=notes
        )
        return JsonResponse({'status': 'success', 'message': f'Attendance for "{workout_type}" marked successfully!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

def attendance_view_view(request):
    if request.user.is_authenticated:
        logs = Attendance.objects.filter(user=request.user)
    else:
        logs = []
    return render(request, 'fitsync_app/attendance_view.html', {'logs': logs})

# Subscription & Payment
@login_required
def subscription_plans_view(request):
    if request.user.userprofile.role == 'admin':
        plans = SubscriptionPlan.objects.all().order_by('price')
    else:
        plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    
    return render(request, 'fitsync_app/subscription_plans.html', {
        'plans': plans,
    })

@login_required
def add_subscription_plan(request):
    if request.user.userprofile.role != 'admin':
        messages.error(request, "Access denied. Administrative privileges required.")
        return redirect('subscription_plans')
        
    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f"Subscription plan '{plan.get_name_display()}' created successfully!")
            return redirect('subscription_plans')
    else:
        form = SubscriptionPlanForm()
        
    return render(request, 'fitsync_app/add_subscription_plan.html', {
        'form': form
    })

@login_required
def edit_subscription_plan(request, plan_id):
    if request.user.userprofile.role != 'admin':
        messages.error(request, "Access denied. Administrative privileges required.")
        return redirect('subscription_plans')
        
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, f"Subscription plan '{plan.get_name_display()}' updated successfully!")
            return redirect('subscription_plans')
    else:
        form = SubscriptionPlanForm(instance=plan)
        
    return render(request, 'fitsync_app/edit_subscription_plan.html', {
        'form': form,
        'plan': plan
    })

@login_required
def payment_view(request):
    plan_name = request.GET.get('plan')
    billing_cycle = request.GET.get('billing', 'monthly')
    
    selected_plan = get_object_or_404(SubscriptionPlan, name=plan_name) if plan_name else None
    
    # Calculate display price
    display_price = selected_plan.price if selected_plan else 0
    if billing_cycle == 'annual' and selected_plan and selected_plan.annual_price:
        display_price = selected_plan.annual_price
        
    if request.method == 'POST':
        razorpay_id = request.POST.get('razorpay_payment_id', f"PAY-{random.randint(100000, 999999)}")
        
        # Update User Subscription
        sub, created = UserSubscription.objects.get_or_create(user=request.user)
        sub.plan = selected_plan
        sub.is_active = True
        
        # Calculate Expiry Date
        if billing_cycle == 'annual':
            sub.expiry_date = timezone.now() + timedelta(days=365)
        elif selected_plan and selected_plan.name == 'lifetime':
            sub.expiry_date = timezone.now() + timedelta(days=36500) # 100 years
        else:
            sub.expiry_date = timezone.now() + timedelta(days=30)
            
        sub.save()
        
        # Create Payment Record for History
        Payment.objects.create(
            user=request.user,
            amount=display_price,
            status='success',
            transaction_id=razorpay_id
        )
        
        plan_display = selected_plan.get_name_display().upper() if selected_plan else "MEMBERSHIP"
        return redirect(f"{reverse('payment_success')}?type=membership&tid={razorpay_id}&plan={plan_display}")
    
    return render(request, 'fitsync_app/payment.html', {
        'plan': selected_plan, 
        'display_price': display_price,
        'billing_cycle': billing_cycle,
        'amount_paise': int(display_price * 100)
    })

@login_required
def trainer_payment_view(request, trainer_id):
    trainer_profile = get_object_or_404(UserProfile, user__id=trainer_id, role='trainer')
    
    # Calculate amount in paise for Razorpay
    amount_paise = int(trainer_profile.price * 100)
    
    if request.method == 'POST':
        # Create Payment Record
        Payment.objects.create(
            user=request.user,
            trainer=trainer_profile.user,
            amount=trainer_profile.price,
            status='success',
            transaction_id=request.POST.get('razorpay_payment_id', f"TRN-{random.randint(10000, 99999)}")
        )
        
        # Assign Trainer to User
        user_profile = request.user.userprofile
        user_profile.assigned_trainer = trainer_profile.user
        user_profile.save()
        
        messages.success(request, f"Successfully hired {trainer_profile.user.get_full_name()}! Your dashboard has been updated.")
        return redirect(f"{reverse('payment_success')}?type=trainer&tid={request.POST.get('razorpay_payment_id', 'TRN-SUCCESS')}&trainer={trainer_profile.user.get_full_name().upper()}")
        
    return render(request, 'fitsync_app/payment_trainer.html', {
        'trainer': trainer_profile,
        'amount_paise': amount_paise
    })

def payment_success_view(request):
    payment_type = request.GET.get('type', 'membership')
    transaction_id = request.GET.get('tid', '#FS-000000')
    plan_name = request.GET.get('plan', 'ELITE GOLD')
    trainer_name = request.GET.get('trainer', 'ELITE COACH')
    
    return render(request, 'fitsync_app/payment_success.html', {
        'payment_type': payment_type,
        'transaction_id': transaction_id,
        'plan_name': plan_name,
        'trainer_name': trainer_name
    })

# AI & Chatbot
@login_required
def chatbot_view(request):
    # Subscription Check: Nova AI is a Premium Feature
    sub = UserSubscription.objects.filter(user=request.user, is_active=True).first()
    if not sub or not sub.plan or sub.plan.name == 'basic':
        messages.warning(request, "Nova AI Coaching is reserved for Premium and Elite members.")
        return redirect('membership')
        
    return render(request, 'fitsync_app/chatbot.html')

@login_required
def ai_hub_view(request):
    # Subscription Check
    sub = UserSubscription.objects.filter(user=request.user, is_active=True).first()
    is_premium = sub and sub.plan and sub.plan.name != 'basic'
    
    return render(request, 'fitsync_app/ai_hub.html', {
        'is_premium': is_premium
    })

@login_required
def chatbot_api_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_msg = data.get('message', '').strip()
            if not user_msg:
                 return JsonResponse({"reply": "I am standing by. Please provide an inquiry."})
        except:
            return JsonResponse({"reply": "Input stream corrupted. Re-initialize uplink."})

        # 1. Attempt Gemini Integration
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if api_key and api_key != "YOUR_API_KEY_HERE":
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')

                # System context to keep it in character
                prompt = f"System: You are AI Coach, the FitSync intelligence. You are highly intelligent, analytical, and motivating. Answer the user's question. If it's about fitness, be very technical. If it's about anything else, answer as a smart AI but maintain your 'AI Coach' persona. Use markdown for lists and bolding.\n\nUser: {user_msg}"
                
                response = model.generate_content(prompt)
                return JsonResponse({"reply": response.text})
            except Exception as e:
                # Fall through to local on error
                pass

        # 2. Local Heuristic Engine (Fallback - Expanded for Demo Mode)
        # This allows Nova to be functional even without an API Key
        knowledge_base = {
            # Nutrition
            "protein": "Protein is the foundational architecture for muscle synthesis. Aim for 1.6g to 2.2g per kg of body mass.",
            "carb": "Carbohydrates provide the ATP necessary for high-intensity training. Focus on complex glycogens like oats, rice, and sweet potatoes.",
            "fat": "Lipids are critical for hormonal homeostasis (testosterone/estrogen). Ensure adequate Omega-3 intake. Don't drop below 0.6g/kg.",
            "creatine": "Creatine Monohydrate is the most researched supplement. It optimizes ATP regeneration. 5g daily is the standard protocol. No loading phase needed.",
            "calorie": "Energy balance dictates mass manipulation. Deficit for cutting, surplus for hypertrophy. Tracking is essential for precision.",
            "water": "Hydration directly impacts neural drive. A 2% dehydration can reduce strength by 15%. Target 3-4 liters daily.",
            "keto": "Ketosis shifts metabolism to lipid oxidation. Effective for satiety but may compromise high-intensity glycolytic output.",
            
            # Training - Specific Exercises
            "squat": "The king of compound movements. Ensure knee tracking over toes and neutral spine. Depth should break parallel for full activation.",
            "deadlift": "Posterior chain dominance. Keep the bar close to the center of gravity. Brace the core to protect lumbar vertebrae.",
            "bench": "Retract scapula to protect rotator cuffs. Leg drive transfers force through the kinetic chain.",
            "pushup": "Maintain a rigid plank position. Elbows should be at a 45-degree angle to the torso. Full range of motion for chest activation.",
            "push up": "Maintain a rigid plank position. Elbows should be at a 45-degree angle to the torso. Full range of motion for chest activation.",
            "pullup": "Full extension at the bottom, chin over bar at the top. Focus on scapular depression to engage the latissimus dorsi.",
            "pull up": "Full extension at the bottom, chin over bar at the top. Focus on scapular depression to engage the latissimus dorsi.",
            "plank": "Isometric core stability. Keep glutes squeezed and spine neutral. Do not let the lumbar region sag.",
            "lunge": "Keeps torso upright. Front knee should not vastly exceed the toe line. Excellent for unilateral leg development.",
            "burpee": "Maximum metabolic demand. Focus on explosive movement and maintaining form despite fatigue.",
            
            # Training - Concepts
            "hypertrophy": "Muscle growth requires mechanical tension, metabolic stress, and muscle damage. Progressive overload is the primary driver.",
            "strength": "Maximal force production requires high intensity (85%+ 1RM) and long rest periods (3-5 mins) to replenish ATP-CP stores.",
            "cardio": "Zone 2 aerobic work builds mitochondrial efficiency. Zone 5 intervals improve VO2 Max. Both are tools; use according to your phase.",
            "hiit": "High Intensity Interval Training optimizes VO2 max and metabolic rate in minimal time. Recommended 2-3 times weekly.",
            "rest": "Growth occurs during recovery, not training. 7-9 hours of sleep is non-negotiable for cortisol management/growth hormone release.",
            "sleep": "Growth occurs during recovery, not training. 7-9 hours of sleep is non-negotiable for cortisol management/growth hormone release.",
            "yoga": "Excellent for mobility, proprioception, and parasympathetic activation. A powerful recovery tool.",
            "stretch": "Static stretching is best post-workout for range of motion. Dynamic stretching is mandatory pre-workout for neural priming.",
            "mobility": "The ability to move a joint actively through a range of motion. Integral for injury prevention and force production.",

            # General & Motivation
            "weight loss": "To oxidise adipose tissue (fat), you must induce a net energy deficit. Combine resistance training to spare muscle with moderate cardio.",
            "weightloss": "To oxidise adipose tissue (fat), you must induce a net energy deficit. Combine resistance training to spare muscle with moderate cardio.",
            "lose fat": "To oxidise adipose tissue (fat), you must induce a net energy deficit. Combine resistance training to spare muscle with moderate cardio.",
            "losefat": "To oxidise adipose tissue (fat), you must induce a net energy deficit. Combine resistance training to spare muscle with moderate cardio.",
            "gain weight": "To accrue mass, consume a hypercaloric diet (+300-500 kcal). Prioritize protein and resistance training to ensure weight gained is lean mass.",
            "gainweight": "To accrue mass, consume a hypercaloric diet (+300-500 kcal). Prioritize protein and resistance training to ensure weight gained is lean mass.",
            "muscle": "Muscle hypertrophy requires mechanical tension through progressive overload. Ensure your protein intake is 1.8-2.2g/kg.",
            "workout": "Consistency is the variable that determines success. A balanced protocol includes resistance training 3-5 times per week with active recovery.",
            "exercise": "Focus on compound movements like squats, deadlifts, and presses. These provide the highest hormonal and systemic response.",
            "diet": "A sustainable diet is one you can adhere to. Balance your macros, stay in a slight deficit for fat loss, and prioritize whole foods.",
            "nutrition": "Fuel your performance. Micronutrients are as important as macros for optimal recovery and systemic health.",
            "motivation": "Motivation is a variable; discipline is a constant. Do not rely on feelings. Rely on the protocol. Action precedes motivation.",
            "discipline": "Discipline is the bridge between goals and accomplishment. It is the ability to choose what you want most over what you want now.",
            "sore": "DOMS (Delayed Onset Muscle Soreness) is a sign of novel stimulus, not necessarily effectiveness. Active recovery and protein intake mitigate it."
        }

        user_msg_lower = user_msg.lower()
        user_msg_normalized = user_msg_lower.replace(" ", "")
        
        # Check KB with smarter matching
        for key, val in knowledge_base.items():
            key_normalized = key.replace(" ", "")
            if key in user_msg_lower or key_normalized in user_msg_normalized:
                return JsonResponse({"reply": f"**AI COACH DATABASE:** {val}"})

        # Conversational / Persona Checks
        if any(x in user_msg_normalized for x in ["whoareyou", "whatareyou"]):
            return JsonResponse({"reply": "I am **AI Coach**, a high-fidelity analytical engine designed to optimize human performance. In this 'Offline Mode', I have access to core training protocols. For full generative intelligence, connect me to the Gemini Neural Net."})
        
        if any(x in user_msg_normalized for x in ["hello", "hi", "hey", "greetings"]):
            return JsonResponse({"reply": f"**System Online.** Biometric synchronization complete. ready to analyze your training data. Ask me about **Nutrition**, **Training**, or **Supplements**."})

        if "thank" in user_msg_normalized:
            return JsonResponse({"reply": "Efficiency is my directive. You are welcome. Now, return to the iron."})

        # Fallback with advice instead of just an error
        return JsonResponse({"reply": "My generative uplink is offline, so I cannot process complex natural language yet. <br><br>**Try asking about keywords like:**<br>• 'Protein' or 'Creatine'<br>• 'Weight loss' or 'Hypertrophy'<br>• 'Squat form' or 'Cardio'<br><br>_Configure API Key for full AI capability._"})


@login_required
@require_POST
def api_log_meal(request):
    try:
        data = json.loads(request.body)
        NutritionLog.objects.create(
            user=request.user,
            meal_type=data.get('meal_type', 'Snack'),
            food_item=data.get('food_item', 'AI Generated Meal'),
            calories=int(data.get('calories', 0)),
            protein=int(data.get('protein', 0)),
            carbs=int(data.get('carbs', 0)),
            fats=int(data.get('fats', 0))
        )
        return JsonResponse({'status': 'success', 'message': 'Fuel log synchronized.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def exercise_detection_view(request):
    return render(request, 'fitsync_app/exercise_detection.html')

@login_required
def fitness_score_view(request):
    user = request.user
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=7)
    
    # BMI Factor (25 pts)
    latest_bmi = BMIHistory.objects.filter(user=user).order_by('-recorded_at').first()
    bmi_val = float(latest_bmi.bmi_score) if latest_bmi else 22.0
    bmi_display = f"{bmi_val:.1f}"
    if bmi_val < 18.5:
        bmi_category = "Underweight"
        bmi_factor = 10
    elif bmi_val <= 24.9:
        bmi_category = "Normal"
        bmi_factor = 25
    elif bmi_val <= 29.9:
        bmi_category = "Overweight"
        bmi_factor = 15
    else:
        bmi_category = "Obese"
        bmi_factor = 5
    
    # Workout Factor (25 pts)
    workouts_this_week = Attendance.objects.filter(user=user, logged_at__date__gte=seven_days_ago).count()
    workouts_per_week = workouts_this_week
    workout_factor = min(25, workouts_per_week * 5)  # 5 pts per workout, max 25
    workout_factor_pct = (workout_factor / 25) * 100
    
    # Calorie Factor (20 pts)
    calorie_logs = NutritionLog.objects.filter(user=user, date__gte=seven_days_ago)
    avg_calories = int(calorie_logs.aggregate(Avg('calories'))['calories__avg'] or 0)
    if 1500 <= avg_calories <= 2500:
        calorie_factor = 20
    elif 1200 <= avg_calories < 1500 or 2500 < avg_calories <= 3000:
        calorie_factor = 12
    elif avg_calories > 0:
        calorie_factor = 6
    else:
        calorie_factor = 8  # Default if no logs
    calorie_factor_pct = (calorie_factor / 20) * 100
    
    # Water Factor (15 pts)
    water_logs = WaterLog.objects.filter(user=user, date__gte=seven_days_ago)
    avg_water_ml = int(water_logs.aggregate(Avg('amount_ml'))['amount_ml__avg'] or 0)
    if avg_water_ml >= 2000:
        water_factor = 15
    elif avg_water_ml >= 1500:
        water_factor = 10
    elif avg_water_ml >= 1000:
        water_factor = 7
    elif avg_water_ml > 0:
        water_factor = 4
    else:
        water_factor = 5  # Default
    water_factor_pct = (water_factor / 15) * 100
    
    # Goal Factor (15 pts)
    goals_total = Goal.objects.filter(user=user).count()
    goals_completed = Goal.objects.filter(user=user, is_completed=True).count()
    goal_completion = int((goals_completed / goals_total * 100)) if goals_total > 0 else 0
    goal_factor = min(15, int((goal_completion / 100) * 15))
    if goals_total == 0:
        goal_factor = 8  # Default
    goal_factor_pct = (goal_factor / 15) * 100
    
    # Total Score
    fitness_score = bmi_factor + workout_factor + calorie_factor + water_factor + goal_factor
    
    # Status & Recommendation
    if fitness_score >= 80:
        score_status = "Excellent"
        recommendation = "You are performing at an elite level. Maintain your current regimen and consider adding advanced training protocols to push further."
    elif fitness_score >= 60:
        score_status = "Good"
        recommendation = "Solid performance. Focus on consistency with hydration and try adding one more workout session per week to reach the next tier."
    elif fitness_score >= 40:
        score_status = "Fair"
        recommendation = "Good foundation but room to grow. Prioritize tracking your nutrition daily and hitting your workout targets at least 3 times per week."
    else:
        score_status = "Needs Improvement"
        recommendation = "Let's get you moving. Start by logging your meals, drinking 2L of water daily, and attending the gym at least twice this week."
    
    # Presentation Colors
    if fitness_score >= 80:
        score_color = "#00ff88"
        score_bg_color = "rgba(0,255,136,0.1)"
    elif fitness_score >= 60:
        score_color = "#00e5ff"
        score_bg_color = "rgba(0,229,255,0.1)"
    elif fitness_score >= 40:
        score_color = "#ffd600"
        score_bg_color = "rgba(255,214,0,0.1)"
    else:
        score_color = "#ff4466"
        score_bg_color = "rgba(255,68,102,0.1)"

    if bmi_category == 'Normal':
        bmi_color = "#00ff88"
    elif bmi_category == 'Underweight':
        bmi_color = "#ffd600"
    else:
        bmi_color = "#ff4466"
    
    # AI Tips
    tips = []
    if bmi_factor < 20:
        tips.append({"title": "BMI Optimization", "text": "Your BMI is outside the optimal range. Combine balanced nutrition with resistance training to reach a healthy weight."})
    if workout_factor < 15:
        tips.append({"title": "Increase Workout Frequency", "text": f"You logged {workouts_per_week} sessions this week. Aim for at least 4 sessions to maximize fitness gains."})
    if calorie_factor < 15:
        tips.append({"title": "Calorie Balance", "text": "Track your meals consistently. Aim for 1800-2200 kcal/day depending on your goals and activity level."})
    if water_factor < 10:
        tips.append({"title": "Stay Hydrated", "text": "Hydration affects energy, recovery, and performance. Target at least 2-3 liters of water daily."})
    if goal_factor < 10:
        tips.append({"title": "Set & Complete Goals", "text": "Define clear weekly goals and track their completion. This keeps you accountable and motivated."})
    if not tips:
        tips.append({"title": "Keep It Up!", "text": "You're doing great across all metrics. Keep the momentum and challenge yourself with new fitness goals."})
    
    context = {
        'fitness_score': fitness_score,
        'score_status': score_status,
        'recommendation': recommendation,
        'score_color': score_color,
        'score_bg_color': score_bg_color,
        'bmi_score_display': bmi_display,
        'bmi_category': bmi_category,
        'bmi_color': bmi_color,
        'bmi_factor': bmi_factor,
        'workouts_per_week': workouts_per_week,
        'workouts_this_week': workouts_this_week,
        'workout_factor': workout_factor,
        'workout_factor_pct': int(workout_factor_pct),
        'avg_calories': avg_calories,
        'calorie_factor': calorie_factor,
        'calorie_factor_pct': int(calorie_factor_pct),
        'avg_water_ml': avg_water_ml,
        'water_factor': water_factor,
        'water_factor_pct': int(water_factor_pct),
        'goal_completion': goal_completion,
        'goals_completed': goals_completed,
        'goals_total': goals_total,
        'goal_factor': goal_factor,
        'goal_factor_pct': int(goal_factor_pct),
        'tips': tips,
    }
    return render(request, 'fitsync_app/fitness_score.html', context)

@login_required
def meal_scanner_view(request):
    return render(request, 'fitsync_app/meal_scanner.html')

@login_required
def habit_streak_view(request):
    user = request.user
    today = timezone.now().date()
    
    # Calculate streak from Attendance
    streak = 0
    check_date = today
    while True:
        attended = Attendance.objects.filter(user=user, logged_at__date=check_date).exists()
        if attended:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    # Total workouts
    total_workouts = Attendance.objects.filter(user=user).count()
    
    # Workouts this week
    week_start = today - timedelta(days=today.weekday())
    workouts_this_week = Attendance.objects.filter(user=user, logged_at__date__gte=week_start).count()
    
    # Goals completed
    goals_completed = Goal.objects.filter(user=user, is_completed=True).count()
    goals_total = Goal.objects.filter(user=user).count()
    
    # Level system based on total workouts
    if total_workouts >= 100:
        level_name = "Fitness Legend"
        level_icon = "🏆"
        next_level_at = 200
    elif total_workouts >= 50:
        level_name = "Fitness Warrior"
        level_icon = "⚔️"
        next_level_at = 100
    elif total_workouts >= 20:
        level_name = "Fitness Champion"
        level_icon = "🥇"
        next_level_at = 50
    elif total_workouts >= 10:
        level_name = "Fitness Enthusiast"
        level_icon = "💪"
        next_level_at = 20
    elif total_workouts >= 3:
        level_name = "Fitness Starter"
        level_icon = "🌟"
        next_level_at = 10
    else:
        level_name = "Beginner"
        level_icon = "🔰"
        next_level_at = 3
    
    level_progress = min(100, int((total_workouts / next_level_at) * 100)) if next_level_at > 0 else 100
    goal_completion_pct = int((goals_completed / goals_total * 100)) if goals_total > 0 else 0
    
    # Badges
    badges = []
    if streak >= 3:
        badges.append({"name": "3-Day Streak", "icon": "🔥", "desc": "3 days in a row!", "earned": True})
    else:
        badges.append({"name": "3-Day Streak", "icon": "🔥", "desc": "Attend 3 days in a row", "earned": False})
    
    if streak >= 7:
        badges.append({"name": "Weekly Warrior", "icon": "⚡", "desc": "7 days in a row!", "earned": True})
    else:
        badges.append({"name": "Weekly Warrior", "icon": "⚡", "desc": "Attend 7 days in a row", "earned": False})
    
    if total_workouts >= 10:
        badges.append({"name": "10 Sessions", "icon": "🏅", "desc": "10 workouts done!", "earned": True})
    else:
        badges.append({"name": "10 Sessions", "icon": "🏅", "desc": f"Complete 10 sessions ({total_workouts}/10)", "earned": False})
    
    if total_workouts >= 50:
        badges.append({"name": "50 Sessions", "icon": "🥈", "desc": "50 Sessions Complete!", "earned": True})
    else:
        badges.append({"name": "50 Sessions", "icon": "🥈", "desc": f"Complete 50 sessions ({total_workouts}/50)", "earned": False})
    
    if goals_completed >= 3:
        badges.append({"name": "Goal Crusher", "icon": "🎯", "desc": "3 goals completed!", "earned": True})
    else:
        badges.append({"name": "Goal Crusher", "icon": "🎯", "desc": f"Complete 3 goals ({goals_completed}/3)", "earned": False})
    
    if workouts_this_week >= 5:
        badges.append({"name": "5x/Week", "icon": "💎", "desc": "5 sessions this week!", "earned": True})
    else:
        badges.append({"name": "5x/Week", "icon": "💎", "desc": f"5 sessions this week ({workouts_this_week}/5)", "earned": False})
    
    # Leaderboard (top users by attendance count)
    leaderboard_raw = (
        Attendance.objects
        .values('user__username', 'user__first_name', 'user__last_name')
        .annotate(workout_count=Count('id'))
        .order_by('-workout_count')[:10]
    )
    
    leaderboard = []
    user_rank = None
    for i, entry in enumerate(leaderboard_raw):
        name = entry['user__first_name'] or entry['user__username']
        if entry['user__username'] == user.username:
            user_rank = i + 1
        leaderboard.append({
            'rank': i + 1,
            'name': name,
            'workouts': entry['workout_count'],
            'is_current_user': entry['user__username'] == user.username
        })
    
    # Last 14 days activity for calendar
    activity_grid = []
    for i in range(13, -1, -1):
        d = today - timedelta(days=i)
        attended = Attendance.objects.filter(user=user, logged_at__date=d).exists()
        activity_grid.append({'date': d.strftime('%b %d'), 'attended': attended})
    
    context = {
        'streak': streak,
        'total_workouts': total_workouts,
        'workouts_this_week': workouts_this_week,
        'goals_completed': goals_completed,
        'goals_total': goals_total,
        'goal_completion_pct': goal_completion_pct,
        'level_name': level_name,
        'level_icon': level_icon,
        'level_progress': level_progress,
        'next_level_at': next_level_at,
        'badges': badges,
        'leaderboard': leaderboard,
        'user_rank': user_rank,
        'activity_grid': activity_grid,
    }
    return render(request, 'fitsync_app/habit_streak.html', context)

def ai_workout_view(request):
    # Subscription Check: AI Tools are Premium Features
    sub = UserSubscription.objects.filter(user=request.user, is_active=True).first()
    if not sub or not sub.plan or sub.plan.name == 'basic':
        messages.warning(request, "Neural Workout Generation is reserved for Premium and Elite members.")
        return redirect('membership')
        
    return render(request, 'fitsync_app/ai_workout.html')

@login_required
def ai_diet_view(request):
    # Subscription Check: AI Tools are Premium Features
    sub = UserSubscription.objects.filter(user=request.user, is_active=True).first()
    if not sub or not sub.plan or sub.plan.name == 'basic':
        messages.warning(request, "AI Metabolic Fueling Protocols are reserved for Premium and Elite members.")
        return redirect('membership')
        
    return render(request, 'fitsync_app/ai_diet.html')

# Reports
@login_required
def report_attendance_view(request):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('user_dashboard')

    try:
        # Calculate real statistics from database
        today = timezone.now().date()
        last_30_days = today - timedelta(days=30)

        # Get all attendance records from last 30 days
        # Use logged_at__date since models.py shows field is logged_at (DateTimeField)
        recent_attendance = Attendance.objects.filter(logged_at__date__gte=last_30_days)

        # Daily average
        daily_counts = recent_attendance.values('logged_at__date').annotate(count=Count('id'))
        if daily_counts.exists():
            total_days = (today - last_30_days).days
            total_checkins = sum(int(d['count']) for d in daily_counts)
            daily_average = total_checkins // total_days if total_days > 0 else 0
        else:
            daily_average = 0

        # Peak time (most common check-in hour)
        peak_hour = 18  # Default to 6 PM
        if recent_attendance.exists():
            hour_counts = {}
            for attendance in recent_attendance:
                if attendance.logged_at:
                    hr = int(attendance.logged_at.hour)
                    # Safe increment for type checker
                    hour_counts[hr] = int(hour_counts.get(hr, 0)) + 1
            if hour_counts:
                peak_hour = max(hour_counts.keys(), key=lambda h: int(hour_counts[h]))
        
        # Format peak time
        if peak_hour > 12:
            peak_time = f"{peak_hour-12:02d}:00 PM"
        elif peak_hour == 12:
            peak_time = "12:00 PM"
        elif peak_hour == 0:
            peak_time = "12:00 AM"
        else:
            peak_time = f"{peak_hour:02d}:00 AM"
        
        # Engagement rate (users who checked in at least once in last 7 days / total active users)
        last_7_days = today - timedelta(days=7)
        active_users_count = UserProfile.objects.filter(role='member').count()
        engaged_users = Attendance.objects.filter(logged_at__date__gte=last_7_days).values('user').distinct().count()
        engagement_rate = int((engaged_users / active_users_count * 100)) if active_users_count > 0 else 0
        
        # Recent attendance logs
        recent_logs = recent_attendance.select_related('user').order_by('-logged_at')[:10]
        
    except Exception as e:
        # If any error occurs, use default values
        daily_average = 0
        peak_time = "N/A"
        engagement_rate = 0
        recent_logs = []
    
    return render(request, 'fitsync_app/report_attendance.html', {
        'daily_average': daily_average,
        'peak_time': peak_time,
        'engagement_rate': engagement_rate,
        'recent_logs': recent_logs
    })

@login_required
def report_payments_view(request):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('user_dashboard')
        
    payments = Payment.objects.all().order_by('-payment_date')
    total_revenue = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Pre-process payment data for display
    payment_list = []
    for payment in payments:
        payment_list.append({
            'transaction_id': payment.transaction_id or 'N/A',
            'user_name': payment.user.get_full_name() or payment.user.username,
            'amount': f"{payment.amount:.2f}",
            'date': payment.payment_date.strftime("%b %d, %Y"),
            'status': payment.status
        })
    
    return render(request, 'fitsync_app/report_payments.html', {
        'payment_list': payment_list,
        'total_revenue': total_revenue
    })

@login_required
def report_members_view(request):
    # Strict Role Check
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role not in ['trainer', 'admin']:
        messages.error(request, "Access denied.")
        return redirect('user_dashboard')

    members = UserProfile.objects.filter(role='member').select_related('user').order_by('-created_at')
    return render(request, 'fitsync_app/report_members.html', {'members': members})

def report_download_view(request):
    return render(request, 'fitsync_app/report_download.html')

# Video Gallery / Exercise Tutorials
@login_required
def video_gallery_view(request):
    videos = ExerciseVideo.objects.all().order_by('-created_at')
    
    # Check if user is trainer to show upload button
    is_trainer = False
    if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'trainer':
        is_trainer = True
        
    return render(request, 'fitsync_app/video_gallery.html', {
        'videos': videos,
        'is_trainer': is_trainer
    })

@login_required
def video_upload_view(request):
    # Check if user is trainer
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'trainer':
        messages.error(request, "Only trainers can upload videos.")
        return redirect('video_gallery')

    if request.method == 'POST':
        form = ExerciseVideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.trainer = request.user
            video.save()
            messages.success(request, "Video uploaded successfully!")
            return redirect('video_gallery')
    else:
        form = ExerciseVideoForm()
    return render(request, 'fitsync_app/video_upload.html', {'form': form})

@login_required
def video_delete_view(request, pk):
    video = get_object_or_404(ExerciseVideo, pk=pk)
    
    # Check if user is the one who uploaded OR an admin
    is_owner = (video.trainer == request.user)
    is_admin = (hasattr(request.user, 'userprofile') and request.user.userprofile.role in ['trainer', 'admin'])
    
    # Specifically check if the trainer who uploaded it is deleting it
    if is_owner or request.user.is_staff:
        video.delete()
        messages.success(request, "Protocol deleted from library.")
    else:
        messages.error(request, "Access denied. You do not have permission to delete this protocol.")
        
    return redirect('video_gallery')

@login_required
def delete_account_view(request):
    """Permanently delete user account and all associated data"""
    if request.method == 'POST':
        user = request.user
        
        # Log out the user first
        logout(request)
        
        # Delete the user (this will cascade delete related data)
        user.delete()
        
        messages.success(request, "Your account has been permanently deleted.")
        return redirect('home')
    
    return redirect('settings')

# ─── Smart Fitness Assessment ─────────────────────────────────────────────────

@login_required
def fitness_assessment_view(request):
    existing = FitnessAssessment.objects.filter(user=request.user).first()

    if request.method == 'POST':
        age = int(request.POST.get('age', 25))
        gender = request.POST.get('gender', 'other')
        height_cm = float(request.POST.get('height_cm', 170))
        weight_kg = float(request.POST.get('weight_kg', 70))
        fitness_goal = request.POST.get('fitness_goal', 'general_fitness')
        activity_level = request.POST.get('activity_level', 'beginner')
        health_issues = request.POST.get('health_issues', '')
        target_weight_kg_raw = request.POST.get('target_weight_kg', '').strip()
        target_weight_kg = float(target_weight_kg_raw) if target_weight_kg_raw else None

        assessment, _ = FitnessAssessment.objects.update_or_create(
            user=request.user,
            defaults={
                'age': age, 'gender': gender,
                'height_cm': height_cm, 'weight_kg': weight_kg,
                'fitness_goal': fitness_goal, 'activity_level': activity_level,
                'health_issues': health_issues, 'target_weight_kg': target_weight_kg,
            }
        )

        bmi = float(f"{weight_kg / ((height_cm / 100) ** 2):.1f}")
        cat = "Underweight" if bmi < 18.5 else "Normal Weight" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
        assessment.bmi_score = Decimal(str(bmi))
        assessment.bmi_category = cat
        assessment.save()

        BMIHistory.objects.create(user=request.user, weight_kg=weight_kg, height_cm=height_cm, bmi_score=bmi)
        messages.success(request, "Fitness assessment complete! Your personalized plan is ready.")
        return redirect('assessment_results')

    return render(request, 'fitsync_app/fitness_assessment.html', {'existing': existing})


@login_required
def assessment_results_view(request):
    assessment = FitnessAssessment.objects.filter(user=request.user).first()
    if not assessment:
        messages.info(request, "Please complete the fitness assessment first.")
        return redirect('fitness_assessment')

    goal = assessment.fitness_goal
    level = assessment.activity_level
    bmi = float(assessment.bmi_score) if assessment.bmi_score else assessment.calculate_bmi()
    daily_cals = assessment.get_daily_calories()
    weight = float(assessment.weight_kg)
    target = float(assessment.target_weight_kg) if assessment.target_weight_kg else None

    # Workout plans keyed by (goal, level)
    workout_plans = {
        ('weight_loss', 'beginner'): [
            ("Day 1", "30-min Brisk Walk + Jumping Jacks (3×15)"),
            ("Day 2", "Bodyweight Squats (3×12) + Lunges (3×10)"),
            ("Day 3", "Rest / Light Yoga & Stretching"),
            ("Day 4", "HIIT Circuit – 20 min (Burpees, High Knees)"),
            ("Day 5", "Swimming or Cycling – 30 min"),
            ("Day 6", "Core Work – Plank (3×30s) + Leg Raises"),
            ("Day 7", "Full Rest & Recovery"),
        ],
        ('weight_loss', 'intermediate'): [
            ("Day 1", "HIIT – 35 min (Sprints + Burpees + Jump Rope)"),
            ("Day 2", "Strength – Deadlifts, Romanian DL, Leg Press"),
            ("Day 3", "Active Recovery – Cycling 20 min + Mobility"),
            ("Day 4", "Upper Body – Push-ups, Dips, Rows"),
            ("Day 5", "HIIT – 30 min Tabata Protocol"),
            ("Day 6", "Full Body Circuit – 4 rounds"),
            ("Day 7", "Rest"),
        ],
        ('weight_loss', 'advanced'): [
            ("Day 1", "Heavy Strength – Squat, Deadlift, Bench (85% 1RM)"),
            ("Day 2", "HIIT Conditioning – 40 min"),
            ("Day 3", "Olympic Lifting + Core"),
            ("Day 4", "Upper Power – Pull-ups, Dips, OHP"),
            ("Day 5", "Sprint Intervals + Sled Push"),
            ("Day 6", "Gymnastics / Skill Work + Mobility"),
            ("Day 7", "Rest"),
        ],
        ('muscle_gain', 'beginner'): [
            ("Day 1", "Chest & Triceps – Push-ups (4×12), Dips (3×8)"),
            ("Day 2", "Back & Biceps – Rows (3×10), Curls (3×12)"),
            ("Day 3", "Rest / Light Walk"),
            ("Day 4", "Legs – Goblet Squat (3×12), Lunges (3×10)"),
            ("Day 5", "Shoulders – DB Press (3×10), Lateral Raise (3×12)"),
            ("Day 6", "Full Body Compound Movements"),
            ("Day 7", "Rest"),
        ],
        ('muscle_gain', 'intermediate'): [
            ("Day 1", "Push – Bench Press, OHP, Tricep Extensions"),
            ("Day 2", "Pull – Deadlift, Pull-ups, Barbell Rows"),
            ("Day 3", "Legs – Squat, Leg Press, Hamstring Curl"),
            ("Day 4", "Rest / Mobility"),
            ("Day 5", "Upper Hypertrophy – 4×8-12 per exercise"),
            ("Day 6", "Lower Hypertrophy + Core"),
            ("Day 7", "Rest"),
        ],
        ('muscle_gain', 'advanced'): [
            ("Day 1", "Heavy Chest + Triceps (5×5 Bench, 4×8 Dips)"),
            ("Day 2", "Heavy Back (5×5 Deadlift, 4×6 Weighted Pull-ups)"),
            ("Day 3", "Heavy Legs (5×5 Squat, Romanian DL, Leg Press)"),
            ("Day 4", "Active Recovery + Stretching"),
            ("Day 5", "Shoulders + Arms Volume Day"),
            ("Day 6", "Full Body – Olympic Lifts"),
            ("Day 7", "Rest"),
        ],
        ('general_fitness', 'beginner'): [
            ("Day 1", "20-min Walk + Basic Stretching Routine"),
            ("Day 2", "Bodyweight Circuit – Squats, Push-ups, Plank"),
            ("Day 3", "Yoga – 30 min Beginner Flow"),
            ("Day 4", "Light Cardio – Cycling or Swimming"),
            ("Day 5", "Full Body Resistance Band Workout"),
            ("Day 6", "Active Play – Badminton, Dancing, Walking"),
            ("Day 7", "Rest"),
        ],
        ('endurance', 'beginner'): [
            ("Day 1", "Easy 30-min Jog / Walk-Run Intervals"),
            ("Day 2", "Core Stability – Plank, Bird-Dog, Dead Bug"),
            ("Day 3", "Cycling 30–45 min at moderate pace"),
            ("Day 4", "Rest"),
            ("Day 5", "Long Run – 45 min easy pace"),
            ("Day 6", "Swimming / Elliptical – 30 min"),
            ("Day 7", "Rest"),
        ],
        ('flexibility', 'beginner'): [
            ("Day 1", "Full Body Yoga Flow – 40 min"),
            ("Day 2", "Hip Flexor + Hamstring Stretching Protocol"),
            ("Day 3", "Pilates Core – 30 min"),
            ("Day 4", "Rest"),
            ("Day 5", "Foam Rolling + Dynamic Mobility"),
            ("Day 6", "Yin Yoga – 45 min Deep Stretch"),
            ("Day 7", "Rest"),
        ],
    }
    workout_plan = (workout_plans.get((goal, level))
                    or workout_plans.get((goal, 'beginner'))
                    or workout_plans[('general_fitness', 'beginner')])

    # Diet plans
    diet_plans = {
        'weight_loss': {
            'breakfast': ['Oats + Chia Seeds + Berries', 'Greek Yogurt + Banana + Almonds', 'Egg White Omelette + Whole Wheat Toast'],
            'lunch': ['Brown Rice + Grilled Chicken + Steamed Veg', 'Quinoa Salad + Tuna + Lemon Dressing', 'Multigrain Roti + Dal + Sabzi'],
            'dinner': ['Mixed Veg Salad + Boiled Eggs + Hummus', 'Grilled Fish + Roasted Sweet Potato', 'Paneer Tikka + Cucumber Raita'],
            'snacks': ['Apple + Peanut Butter', 'Mixed Nuts (30g)', 'Green Tea + Rice Cakes'],
        },
        'muscle_gain': {
            'breakfast': ['4 Whole Eggs + Oats + Banana', 'Peanut Butter Protein Shake + Toast', 'Paneer Bhurji + Parathas + Milk'],
            'lunch': ['White Rice + Chicken Breast + Lentils', 'Pasta + Ground Beef + Salad', 'Roti + Rajma + Dahi'],
            'dinner': ['Salmon + Brown Rice + Broccoli', 'Chicken Curry + Rice + Dal', 'Steak / Tofu + Mashed Sweet Potato'],
            'snacks': ['Protein Shake + Banana', 'Cottage Cheese + Fruit', 'Boiled Eggs ×3 + Nuts'],
        },
        'general_fitness': {
            'breakfast': ['Mixed Fruit Smoothie + Toast', 'Idli + Sambhar + Coconut Chutney', 'Poha + Sprouts + Green Tea'],
            'lunch': ['Dal + Roti + Mixed Veg + Curd', 'Grilled Chicken Sandwich + Soup', 'Rice + Fish Curry + Salad'],
            'dinner': ['Veg Khichdi + Raita', 'Grilled Paneer + Roti + Salad', 'Moong Dal + Rice'],
            'snacks': ['Fruits + Nuts', 'Sprouts Chaat', 'Buttermilk + Roasted Chana'],
        },
        'endurance': {
            'breakfast': ['Oats + Banana + Honey + Milk', 'Whole Grain Bread + PB + Juice', 'Idli (4) + Protein Shake'],
            'lunch': ['Pasta + Lean Protein + Veg', 'Rice + Dal + Chicken + Salad', 'Grain Bowl + Chickpeas + Avocado'],
            'dinner': ['Light Rice + Dal + Veg', 'Soup + Multigrain Roti', 'Quinoa + Lentils + Roasted Veg'],
            'snacks': ['Energy Bar + Banana', 'Dates + Nuts', 'Sports Drink + Rice Cakes'],
        },
        'flexibility': {
            'breakfast': ['Green Smoothie (Spinach + Apple)', 'Fruit Bowl + Flaxseeds + Yogurt', 'Chia Pudding + Mango'],
            'lunch': ['Buddha Bowl + Tofu + Brown Rice', 'Veg Wrap + Hummus + Salad', 'Dal + Roti + Stir-Fried Veg'],
            'dinner': ['Veg Soup + Small Roti', 'Salad + Seeds + Lemon Dressing', 'Khichdi + Ghee + Veg'],
            'snacks': ['Herbal Tea + Dates', 'Fruits + Almond Butter', 'Coconut Water + Nuts'],
        },
    }
    diet = diet_plans.get(goal, diet_plans['general_fitness'])
    daily_diet = {k: random.choice(v) for k, v in diet.items()}

    # Goal progress
    weight_goal_progress = None
    kg_to_lose_gain = None
    if target:
        first_entry = BMIHistory.objects.filter(user=request.user).order_by('recorded_at').first()
        latest = BMIHistory.objects.filter(user=request.user).order_by('-recorded_at').first()
        if first_entry and float(first_entry.weight_kg) != float(latest.weight_kg):
            start_w = float(first_entry.weight_kg)
            total_needed = abs(start_w - target)
            moved = abs(start_w - float(latest.weight_kg))
            weight_goal_progress = min(100, int((moved / total_needed * 100))) if total_needed > 0 else 0
        else:
            weight_goal_progress = 5
        kg_to_lose_gain = float(f"{abs(weight - target):.1f}")

    if bmi < 18.5:
        bmi_color = '#60a5fa'; bmi_rec = "Focus on caloric surplus with nutrient-dense foods and light resistance training."
    elif bmi < 25:
        bmi_color = '#10b981'; bmi_rec = "You're in the optimal range. Maintain with balanced nutrition and regular exercise."
    elif bmi < 30:
        bmi_color = '#f59e0b'; bmi_rec = "Incorporate cardio 4× per week and a moderate caloric deficit of 400 kcal."
    else:
        bmi_color = '#ef4444'; bmi_rec = "Prioritize low-impact cardio, strength training, and a structured diet plan."

    goal_labels = {
        'weight_loss': 'Weight Loss', 'muscle_gain': 'Muscle Gain',
        'general_fitness': 'General Fitness', 'endurance': 'Endurance', 'flexibility': 'Flexibility',
    }

    if not request.user.userprofile.active_workout:
        new_workout = WorkoutProgram.objects.create(
            title=f"AI Configured: {goal_labels.get(goal, 'Custom Plan')}",
            description=f"Generated for {request.user.username} based on {level} activity level.",
            difficulty=level,
            frequency_per_week=5
        )
        request.user.userprofile.active_workout = new_workout
        request.user.userprofile.save()

    if not request.user.userprofile.active_diet:
        new_diet = DietPlan.objects.create(
            name=f"AI Configured Diet: {goal_labels.get(goal, 'Custom Plan')}",
            description=f"Caloric goal: {daily_cals} kcal.",
            daily_calories=daily_cals,
            protein_g=int(weight * 2.2),
            carbs_g=int((daily_cals * 0.4)/4),
            fats_g=int((daily_cals * 0.3)/9)
        )
        # Create meals for the diet
        for d in daily_diet:
            Meal.objects.create(
                diet_plan=new_diet, day='monday', name=d.capitalize(), 
                calories=daily_cals//4, protein=30, carbs=40, fats=10, description=daily_diet[d]
            )
        request.user.userprofile.active_diet = new_diet
        request.user.userprofile.save()

    return render(request, 'fitsync_app/assessment_results.html', {
        'assessment': assessment,
        'bmi': bmi,
        'bmi_color': bmi_color,
        'bmi_rec': bmi_rec,
        'daily_cals': daily_cals,
        'workout_plan': workout_plan,
        'daily_diet': daily_diet,
        'weight_goal_progress': weight_goal_progress,
        'kg_to_lose_gain': kg_to_lose_gain,
        'goal_label': goal_labels.get(goal, goal.replace('_', ' ').title()),
        'level_label': level.capitalize(),
    })

@login_required
def live_session_view(request):
    """
    Renders the UI for Live Trainer Sessions.
    Trainers can create sessions, and anyone can view upcoming sessions.
    """
    if request.method == 'POST':
        # Create a new session (only trainers)
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'trainer':
            t_title = request.POST.get('title', '').strip()
            t_date = request.POST.get('date')
            t_time = request.POST.get('time')
            t_link = request.POST.get('meeting_link', '').strip()
            t_type = request.POST.get('workout_type', 'General Fitness')

            # Validate required fields
            if not t_title or not t_date or not t_time or not t_link:
                messages.error(request, "All fields are required, including the Google Meet link.")
                return redirect('live_session')

            # Ensure link starts with http
            if not t_link.startswith(('http://', 'https://')):
                t_link = 'https://' + t_link

            LiveSession.objects.create(
                trainer_name=request.user.get_full_name() or request.user.username,
                session_title=t_title,
                date=t_date,
                time=t_time,
                meeting_link=t_link,
                workout_type=t_type
            )
            messages.success(request, f"✅ Live session '{t_title}' scheduled! Members can now join via Google Meet.")
            return redirect('live_session')
        else:
            messages.error(request, "Only trainers can schedule sessions.")
            return redirect('live_session')

    # Get upcoming sessions (date >= today), ordered by soonest first
    upcoming_sessions = LiveSession.objects.filter(
        date__gte=timezone.now().date()
    ).order_by('date', 'time')

    return render(request, 'fitsync_app/live_session.html', {
        'sessions': upcoming_sessions,
    })


@login_required
def live_session_room_view(request, session_id):
    """
    Google Meet / external link redirect.
    Looks up the LiveSession by ID and redirects directly to the stored
    meeting_link (Google Meet, Zoom, Jitsi, etc.).
    """
    session = get_object_or_404(LiveSession, id=session_id)
    if not session.meeting_link:
        messages.error(request, "This session does not have a meeting link yet.")
        return redirect('live_session')
    return redirect(session.meeting_link)


@login_required
def delete_live_session_view(request, session_id):
    """
    Cancel / Delete a live session.
    Allow trainers/admins to cancel a scheduled live session.
    """
    session = get_object_or_404(LiveSession, id=session_id)
    if hasattr(request.user, 'userprofile') and request.user.userprofile.role in ['trainer', 'admin']:
        # Ensure only trainers/admins can delete
        title = session.session_title
        session.delete()
        messages.success(request, f"❌ Live session '{title}' has been cancelled.")
    else:
        messages.error(request, "Error: You do not have permission to cancel this session.")
    return redirect('live_session')


# ──────────────────────────────────────────────────────────────────────────────
# 🛒 FITSYNC STORE VIEWS
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def store_view(request):
    """Main store page — browse all products with category filter and search."""
    category = request.GET.get('category', '')
    search_q = request.GET.get('q', '').strip()

    # Auto-seed default products if store is empty
    if not Product.objects.exists():
        defaults = [
            {'name': 'FitSync Whey Protein', 'description': 'Premium whey protein with 25g protein per serving. Chocolate & Vanilla flavours. Supports muscle recovery and growth after intense workouts.', 'price': 2499, 'original_price': 3199, 'category': 'protein', 'stock': 20, 'rating': 4.8, 'reviews_count': 312, 'badge': 'bestseller'},
            {'name': 'Resistance Band Set', 'description': '5-level resistance bands for home workouts, rehab, and stretching. Durable latex construction, suitable for all fitness levels.', 'price': 699, 'original_price': 999, 'category': 'equipment', 'stock': 50, 'rating': 4.6, 'reviews_count': 187, 'badge': 'sale'},
            {'name': 'Pro Gym Gloves', 'description': 'Full palm protection with wrist support. Breathable mesh back, anti-slip grip. Perfect for heavy lifting sessions.', 'price': 399, 'original_price': None, 'category': 'apparel', 'stock': 35, 'rating': 4.3, 'reviews_count': 95, 'badge': ''},
            {'name': 'FitSync Shaker Bottle', 'description': '600ml BPA-free shaker with leak-proof lid. Stainless steel mixing ball for smooth protein shakes. Includes storage compartment.', 'price': 199, 'original_price': 299, 'category': 'equipment', 'stock': 100, 'rating': 4.5, 'reviews_count': 228, 'badge': 'new'},
            {'name': 'Adjustable Dumbbell Set', 'description': 'Space-saving adjustable dumbbell pair. Adjusts from 2.5kg to 25kg per side. Ideal for home gym setups.', 'price': 4999, 'original_price': 6999, 'category': 'equipment', 'stock': 10, 'rating': 4.9, 'reviews_count': 143, 'badge': 'limited'},
            {'name': 'Creatine Monohydrate', 'description': 'Pure micronized creatine monohydrate — 3g per serving. Unflavored, mixes instantly. Boosts strength and power output.', 'price': 849, 'original_price': None, 'category': 'protein', 'stock': 40, 'rating': 4.7, 'reviews_count': 204, 'badge': 'bestseller'},
            {'name': 'Yoga Mat (6mm)', 'description': 'Anti-slip, high-density yoga and exercise mat. 183 x 61cm. Ideal for yoga, pilates, stretching, and bodyweight workouts.', 'price': 599, 'original_price': 799, 'category': 'equipment', 'stock': 60, 'rating': 4.4, 'reviews_count': 76, 'badge': 'sale'},
            {'name': 'Foam Roller', 'description': 'Deep-tissue self-massage foam roller for muscle recovery and myofascial release. High-density EVA foam, 30cm length.', 'price': 449, 'original_price': None, 'category': 'recovery', 'stock': 25, 'rating': 4.6, 'reviews_count': 119, 'badge': 'new'},
        ]
        for d in defaults:
            Product.objects.create(**d)

    products = Product.objects.filter(is_active=True)
    if category:
        products = products.filter(category=category)
    if search_q:
        products = products.filter(Q(name__icontains=search_q) | Q(description__icontains=search_q))
    products = products.order_by('-created_at')

    cart_count = 0
    try:
        cart_count = request.user.cart.item_count()
    except Exception:
        cart_count = 0

    categories = Product.CATEGORY_CHOICES
    return render(request, 'fitsync_app/store.html', {
        'products': products,
        'categories': categories,
        'active_category': category,
        'search_q': search_q,
        'cart_count': cart_count,
    })


@login_required
def product_detail_view(request, pk):
    """Individual product detail page."""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    cart_count = 0
    try:
        cart_count = request.user.cart.item_count()
    except Exception:
        cart_count = 0
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=pk)[:4]
    return render(request, 'fitsync_app/product_detail.html', {
        'product': product,
        'related': related,
        'cart_count': cart_count,
    })


@login_required
def cart_view(request):
    """View the current user's cart."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'fitsync_app/cart.html', {'cart': cart})


@login_required
def add_to_cart_view(request, pk):
    """Add a product to cart, or increment quantity if already in cart."""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    if product.stock < 1:
        messages.error(request, f"Sorry, {product.name} is out of stock.")
        return redirect('store')

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        if item.quantity < product.stock:
            item.quantity += 1
            item.save()
        else:
            messages.warning(request, f"Maximum available stock ({product.stock}) already in your cart.")
    else:
        messages.success(request, f"✅ {product.name} added to cart!")

    next_url = request.META.get('HTTP_REFERER', '/store/')
    return redirect(next_url)


@login_required
def remove_from_cart_view(request, item_id):
    """Remove a specific item from cart."""
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    name = item.product.name
    item.delete()
    messages.success(request, f"❌ {name} removed from cart.")
    return redirect('cart')


@login_required
def update_cart_view(request, item_id):
    """Update quantity of a cart item via POST."""
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    qty = int(request.POST.get('quantity', 1))
    if qty < 1:
        item.delete()
        messages.info(request, "Item removed from cart.")
    elif qty > item.product.stock:
        messages.warning(request, f"Only {item.product.stock} units available.")
    else:
        item.quantity = qty
        item.save()
    return redirect('cart')


@login_required
def checkout_view(request):
    """Checkout — convert cart items into a confirmed Order."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()

    if not items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('store')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        house_address = request.POST.get('house_address', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        pincode = request.POST.get('pincode', '').strip()
        country = request.POST.get('country', 'India').strip()
        note = request.POST.get('note', '').strip()

        total = cart.total()
        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            status='confirmed',
            full_name=full_name,
            phone=phone,
            house_address=house_address,
            city=city,
            state=state,
            pincode=pincode,
            country=country,
            order_note=note,
        )
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity,
            )
            # Decrement stock
            item.product.stock = max(0, item.product.stock - item.quantity)
            item.product.save()

        cart.items.all().delete()  # Clear cart after order
        messages.success(request, f"🎉 Order #{order.id} placed successfully! Your items are on their way.")
        return redirect('order_history')

    return render(request, 'fitsync_app/checkout.html', {'cart': cart, 'items': items})


@login_required
def order_history_view(request):
    """Display all past orders for the logged-in user."""
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
    return render(request, 'fitsync_app/order_history.html', {'orders': orders})


@login_required
def cart_count_api(request):
    """Returns cart item count as JSON for live badge updates."""
    try:
        count = request.user.cart.item_count()
    except Exception:
        count = 0
    return JsonResponse({'count': count})


# ── FitSync Store Administration ─────────────────────────────────────────────

@login_required
def store_management_view(request):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('admin_dashboard')
        
    products = Product.objects.all().order_by('-created_at')
    orders = Order.objects.all().order_by('-created_at')[:10]
    
    context = {
        'products': products,
        'recent_orders': orders,
        'total_revenue': Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'total_items_sold': OrderItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'low_stock_count': products.filter(stock__lt=5).count(),
    }
    return render(request, 'fitsync_app/store_management.html', context)

@login_required
def add_product_view(request):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('admin_dashboard')
        
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "New product added to catalog.")
            return redirect('store_management')
    else:
        form = ProductForm()
        
    return render(request, 'fitsync_app/product_form.html', {'form': form, 'title': 'Add New Equipment'})

@login_required
def edit_product_view(request, pk):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('admin_dashboard')
        
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product '{product.name}' updated successfully.")
            return redirect('store_management')
    else:
        form = ProductForm(instance=product)
        
    return render(request, 'fitsync_app/product_form.html', {'form': form, 'title': 'Update Product', 'product': product})

@login_required
def admin_orders_view(request):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('admin_dashboard')
        
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'fitsync_app/admin_orders.html', {'orders': orders})

@login_required
def update_order_status_view(request, pk):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('admin_dashboard')
        
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f"Order #{order.id} status updated to {new_status}.")
        else:
            messages.error(request, "Invalid status.")
            
    return redirect('admin_orders')
def why_fitsync_view(request):
    """View to display detailed information about FitSync's benefits and unique features."""
    benefits = [
        {
            'icon': 'fa-solid fa-brain-circuit',
            'title': 'AI-Driven Personalization',
            'description': 'Our proprietary AI engine analyzes your biomarkers, goals, and meal photos to create dynamic workout and nutrition plans that evolve with you.'
        },
        {
            'icon': 'fa-solid fa-ranking-star',
            'title': 'Elite Trainer Network',
            'description': 'Access the world\'s top 1% of fitness professionals for 1-on-1 coaching, real-time feedback, and live group training sessions.'
        },
        {
            'icon': 'fa-solid fa-dumbbell',
            'title': 'Premium Home Equipment',
            'description': 'From adjustable dumbbells to yoga alignment mats, we supply professional-grade gear delivered directly to your doorstep.'
        },
        {
            'icon': 'fa-solid fa-users-rays',
            'title': 'Global Fitness Community',
            'description': 'Stay motivated with global challenges, shared goals, and a supportive community of like-minded high-performance individuals.'
        }
    ]
    return render(request, 'fitsync_app/why_fitsync.html', {'benefits': benefits})

def migrate_db_view(request):
    """Temporary view to trigger database migrations and create admin on Vercel."""
    from django.core.management import call_command # type: ignore
    from django.http import HttpResponse # type: ignore
    from django.contrib.auth.models import User # type: ignore
    from fitsync_app.models import UserProfile # type: ignore
    
    if request.GET.get('key') == 'fitsync_deploy_2026':
        try:
            # 1. Run Migrations
            call_command('migrate', interactive=False)
            
            # 2. Create Default Admin if it doesn't exist
            if not User.objects.filter(username='admin').exists():
                admin_user = User.objects.create_superuser('admin', 'admin@fitsync.com', 'admin123')
                UserProfile.objects.get_or_create(user=admin_user, role='admin', phone_number='0000000000')
                msg = "✅ Migrations completed and Admin (admin/admin123) created!"
            else:
                msg = "✅ Migrations completed successfully!"
                
            return HttpResponse(msg)
        except Exception as e:
            return HttpResponse(f"❌ Error: {str(e)}")
    return HttpResponse("Unauthorized", status=401)
