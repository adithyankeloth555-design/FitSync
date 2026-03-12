"""
Management command: send_goal_reminders
Run daily (via cron / Windows Task Scheduler) to email users whose goal
deadline is exactly 3 days away and the goal is not yet completed.

Usage:
    python manage.py send_goal_reminders
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from fitsync_app.models import Goal


class Command(BaseCommand):
    help = "Send email reminders for goals due in 3 days"

    def handle(self, *args, **options):
        today = timezone.now().date()
        target_date = today + timedelta(days=3)

        # Goals that expire in 3 days and are not yet complete
        pending_goals = Goal.objects.filter(
            target_date=target_date,
            is_completed=False,
        ).select_related('user')

        sent = 0
        failed = 0

        for goal in pending_goals:
            user = goal.user
            if not user.email:
                continue

            days_left = (goal.target_date - today).days
            subject = f"⏰ FitSync Reminder: '{goal.title}' is due in {days_left} days!"
            message = f"""Hi {user.first_name or user.username},

This is a friendly reminder from FitSync Elite 💪

Your fitness goal is approaching its deadline:

━━━━━━━━━━━━━━━━━━━━━━━
🎯 Goal:       {goal.title}
📅 Deadline:   {goal.target_date.strftime('%B %d, %Y')}
⏳ Days Left:  {days_left} days
📊 Progress:   {goal.get_progress_percent():.0f}% complete
━━━━━━━━━━━━━━━━━━━━━━━

Don't give up — you're almost there! Visit your Goals page to update your progress:
👉 https://fit-sync-roan.vercel.app/goals/

Keep pushing,
The FitSync Elite Team
"""
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                sent += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Reminder sent to {user.email} for goal: '{goal.title}'")
                )
            except Exception as e:
                failed += 1
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Failed to send to {user.email}: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Sent: {sent} | Failed: {failed} | Total goals checked: {pending_goals.count()}"
            )
        )
