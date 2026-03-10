# pyre-ignore-all-errors[21]
from django.urls import path # pyre-ignore[21]
from django.views.generic.base import RedirectView # pyre-ignore[21]
from . import views # pyre-ignore[21]
from . import views_help # pyre-ignore[21]

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('trainer/login/', views.trainer_login_view, name='trainer_login'),
    path('admin/login/', views.admin_login_view, name='admin_login'),
    path('admin_login.html', RedirectView.as_view(url='/admin/login/')), # Handle direct filename access
    path('signup/', views.signup_view, name='signup'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Dashboard
    path('', views.home_view, name='home'),
    path('admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('adminhome', RedirectView.as_view(url='/admin/')), 
    path('admin_dashboard/', RedirectView.as_view(url='/admin/')), 
    path('dashboard/admin/', RedirectView.as_view(url='/admin/')), 
    path('dashboard/trainer/', views.trainer_dashboard_view, name='trainer_dashboard'),
    path('dashboard/user/', views.user_dashboard_view, name='user_dashboard'),
    path('trainers/', views.trainer_list_view, name='trainer_list'),
    path('trainers/add/', views.add_trainer_view, name='add_trainer'),
    path('trainers/delete/<int:trainer_id>/', views.delete_trainer_view, name='delete_trainer'),
    
    # New Dashboard Features
    path('progress/', views.progress_view, name='progress'),
    path('trainer/member/<int:user_id>/progress/', views.trainer_member_progress_view, name='trainer_member_progress'),
    path('attendance/', views.attendance_tracker_view, name='attendance'),
    path('membership/', views.membership_view, name='membership'),
    path('nutrition/', views.nutrition_view, name='nutrition'),
    path('api/nutrition/water/add/', views.add_water, name='add_water'),
    path('goals/', views.goals_view, name='goals'),
    path('messages/', views.messages_view, name='messages'),
    path('settings/', views.settings_view, name='settings'),
    path('help/', views.help_view, name='help'),
    path('community/', views.community_view, name='community'),

    # Diet
    path('diet/', views.diet_list_view, name='diet_list'),
    path('diet/<int:pk>/', views.diet_detail_view, name='diet_detail'),
    path('diet/add/', views.diet_add_view, name='diet_add'),
    path('diet/<int:diet_id>/meal/add/', views.meal_add_view, name='meal_add'),
    path('diet/<int:pk>/edit/', views.diet_edit_view, name='diet_edit'),
    path('diet/<int:pk>/delete/', views.diet_delete_view, name='diet_delete'),
    path('meal/<int:meal_id>/delete/', views.meal_delete_view, name='meal_delete'),

    # Workout
    path('workout/', views.workout_list_view, name='workout_list'),
    path('workout/session/<int:pk>/', views.workout_session_view, name='workout_session'),
    path('workout/add/', views.workout_add_view, name='workout_add'),
    path('workout/edit/', views.workout_edit_view, name='workout_edit'),

    # BMI
    path('bmi/calculator/', views.bmi_calculator_view, name='bmi_calculator'),
    path('bmi/history/', views.bmi_history_view, name='bmi_history'),

    # Attendance
    path('attendance/mark/', views.attendance_mark_view, name='attendance_mark'),
    path('api/attendance/mark/', views.mark_attendance_api, name='mark_attendance_api'),
    path('attendance/view/', views.attendance_view_view, name='attendance_view'),

    # Subscription & Payment
    path('subscription/', views.subscription_plans_view, name='subscription_plans'),
    path('subscription/add/', views.add_subscription_plan, name='add_subscription_plan'),
    path('subscription/edit/<int:plan_id>/', views.edit_subscription_plan, name='edit_subscription_plan'),
    path('payment/', views.payment_view, name='payment'),
    path('payment/trainer/<int:trainer_id>/', views.trainer_payment_view, name='trainer_payment'),
    path('payment/success/', views.payment_success_view, name='payment_success'),

    # AI & Chatbot
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('ai-hub/', views.ai_hub_view, name='ai_hub'),
    path('api/chatbot/', views.chatbot_api_view, name='chatbot_api'),
    path('api/nutrition/log/', views.api_log_meal, name='api_log_meal'),
    path('ai-workout/', views.ai_workout_view, name='ai_workout'),
    path('ai-diet/', views.ai_diet_view, name='ai_diet'),
    
    # Advanced AI Features
    path('exercise-detection/', views.exercise_detection_view, name='exercise_detection'),
    path('fitness-score/', views.fitness_score_view, name='fitness_score'),
    path('meal-scanner/', views.meal_scanner_view, name='meal_scanner'),
    path('habit-streak/', views.habit_streak_view, name='habit_streak'),

    # Smart Fitness Assessment
    path('fitness-assessment/', views.fitness_assessment_view, name='fitness_assessment'),
    path('assessment-results/', views.assessment_results_view, name='assessment_results'),

    # Live Sessions
    path('live-session/', views.live_session_view, name='live_session'),
    path('live-session/room/<int:session_id>/', views.live_session_room_view, name='live_session_room'),
    path('live-session/delete/<int:session_id>/', views.delete_live_session_view, name='delete_live_session'),

    # Reports
    path('reports/attendance/', views.report_attendance_view, name='report_attendance'),
    path('reports/payments/', views.report_payments_view, name='report_payments'),
    path('reports/members/', views.report_members_view, name='report_members'),
    path('reports/download/', views.report_download_view, name='report_download'),
    
    # Video Gallery
    path('videos/', views.video_gallery_view, name='video_gallery'),
    path('videos/upload/', views.video_upload_view, name='video_upload'),
    path('videos/delete/<int:pk>/', views.video_delete_view, name='video_delete'),
    
    # Help Center Admin
    path('admin/help-tickets/', views_help.admin_help_tickets_view, name='admin_help_tickets'),
    
    # Account Management
    path('account/delete/', views.delete_account_view, name='delete_account'),

    # ── FitSync Store ────────────────────────────────────────────────────────
    path('store/', views.store_view, name='store'),
    path('store/product/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('store/cart/', views.cart_view, name='cart'),
    path('store/cart/add/<int:pk>/', views.add_to_cart_view, name='add_to_cart'),
    path('store/cart/remove/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('store/cart/update/<int:item_id>/', views.update_cart_view, name='update_cart'),
    path('store/checkout/', views.checkout_view, name='checkout'),
    path('store/orders/', views.order_history_view, name='order_history'),
    path('api/cart/count/', views.cart_count_api, name='cart_count_api'),

    # Admin Store Management
    path('store/manage/', views.store_management_view, name='store_management'),
    path('store/product/add/', views.add_product_view, name='add_product'),
    path('store/product/<int:pk>/edit/', views.edit_product_view, name='edit_product'),
    path('store/admin/orders/', views.admin_orders_view, name='admin_orders'),
    path('store/admin/order/<int:pk>/status/', views.update_order_status_view, name='update_order_status'),

    # Brand Details
    path('why-fitsync/', views.why_fitsync_view, name='why_fitsync'),
    path('migrate/', views.migrate_db_view, name='migrate_db'),
]
