# pyre-ignore-all-errors[21]
from django.contrib import admin # type: ignore
from fitsync_app.models import ( # type: ignore
    UserProfile, DietPlan, WorkoutProgram, Attendance, Payment, Goal,
    NutritionLog, Message, CommunityPost, CommunityComment, Notification,
    BMIHistory, ExerciseVideo, WaterLog, TrainerFeedback, EmailOTP,
    LiveSession, FitnessAssessment, HelpTicket, Meal,
    Product, Cart, CartItem, Order, OrderItem
)

# ── Existing Models ──────────────────────────────────────────────────────────
admin.site.register(UserProfile)
admin.site.register(DietPlan)
admin.site.register(WorkoutProgram)
admin.site.register(Attendance)
admin.site.register(Payment)
admin.site.register(Goal)
admin.site.register(NutritionLog)
admin.site.register(Message)
admin.site.register(CommunityPost)
admin.site.register(CommunityComment)
admin.site.register(Notification)
admin.site.register(BMIHistory)
admin.site.register(ExerciseVideo)
admin.site.register(WaterLog)
admin.site.register(TrainerFeedback)
admin.site.register(EmailOTP)
admin.site.register(LiveSession)
admin.site.register(FitnessAssessment)
admin.site.register(HelpTicket)
admin.site.register(Meal)

# ── Store Models ─────────────────────────────────────────────────────────────
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ('name', 'category', 'price', 'original_price', 'stock', 'badge', 'is_active', 'created_at')
    list_filter   = ('category', 'badge', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock', 'is_active', 'badge')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ('id', 'user', 'total_amount', 'status', 'created_at')
    list_filter   = ('status',)
    search_fields = ('user__username',)
    list_editable = ('status',)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

admin.site.register(OrderItem)

