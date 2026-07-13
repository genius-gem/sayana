"""
reminder_service.py

Automatically checks all reminders
and sends notifications.
"""

from datetime import date, timedelta

from models.user import User
from models.reminder import Reminder

from services.email_service import EmailService
from services.whatsapp_service import WhatsAppService


class ReminderService:

    @staticmethod
    def process_reminders():

        today = date.today()

        reminders = Reminder.query.all()

        print("=" * 60)
        print("Checking reminders...")
        print("=" * 60)

        for reminder in reminders:

            user = reminder.user

            if user is None:
                continue

            if not user.is_active:
                continue

            due_date = reminder.next_injection_date

            days_remaining = (due_date - today).days

            print(
                f"{user.full_name} -> {days_remaining} day(s)"
            )

            # =====================================
            # 7 DAYS
            # =====================================

            if days_remaining == 7:

                ReminderService.send_notifications(

                    user,

                    reminder,

                    "seven"

                )

            # =====================================
            # 3 DAYS
            # =====================================

            elif days_remaining == 3:

                ReminderService.send_notifications(

                    user,

                    reminder,

                    "three"

                )

            # =====================================
            # TOMORROW
            # =====================================

            elif days_remaining == 1:

                ReminderService.send_notifications(

                    user,

                    reminder,

                    "tomorrow"

                )

            # =====================================
            # TODAY
            # =====================================

            elif days_remaining == 0:

                ReminderService.send_notifications(

                    user,

                    reminder,

                    "today"

                )

            # =====================================
            # MISSED
            # =====================================

            elif days_remaining < 0:

                ReminderService.send_notifications(

                    user,

                    reminder,

                    "missed"

                )

        print("=" * 60)
        print("Reminder check completed.")
        print("=" * 60)

    # =====================================================

    @staticmethod
    def send_notifications(

        user,

        reminder,

        reminder_type

    ):

        # --------------------------
        # EMAIL
        # --------------------------

        if user.email_enabled:

            if reminder_type == "seven":

                EmailService.send_seven_days(

                    user,

                    reminder

                )

            elif reminder_type == "three":

                EmailService.send_three_days(

                    user,

                    reminder

                )

            elif reminder_type == "tomorrow":

                EmailService.send_tomorrow(

                    user,

                    reminder

                )

            elif reminder_type == "today":

                EmailService.send_due_today(

                    user,

                    reminder

                )

            elif reminder_type == "missed":

                EmailService.send_missed(

                    user,

                    reminder

                )

        # --------------------------
        # WHATSAPP
        # --------------------------

        if user.whatsapp_enabled:

            if reminder_type == "seven":

                WhatsAppService.send_seven_days(

                    user,

                    reminder

                )

            elif reminder_type == "three":

                WhatsAppService.send_three_days(

                    user,

                    reminder

                )

            elif reminder_type == "tomorrow":

                WhatsAppService.send_tomorrow(

                    user,

                    reminder

                )

            elif reminder_type == "today":

                WhatsAppService.send_due_today(

                    user,

                    reminder

                )

            elif reminder_type == "missed":

                WhatsAppService.send_missed(

                    user,

                    reminder
                )