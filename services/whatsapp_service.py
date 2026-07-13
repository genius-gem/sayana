"""
whatsapp_service.py

Handles WhatsApp reminder delivery.

Currently this service logs reminders.

Later you can connect it to:

- Twilio WhatsApp API
- Meta WhatsApp Cloud API
- Africa's Talking
- Termii
"""

from datetime import datetime

from config.database import db
from models.reminder_log import ReminderLog


class WhatsAppService:

    @staticmethod
    def send_reminder(
        user,
        reminder,
        message,
        reminder_type="General Reminder"
    ):
        """
        Sends a WhatsApp reminder.

        Currently this simulates sending
        and stores the log.
        """

        log = ReminderLog(

            user_id=user.id,

            reminder_id=reminder.id,

            channel="WhatsApp",

            reminder_type=reminder_type,

            status="Pending",

            message=message

        )

        db.session.add(log)
        db.session.commit()

        try:

            # =====================================
            # FUTURE WHATSAPP API GOES HERE
            #
            # Example:
            #
            # twilio.messages.create(...)
            #
            # or
            #
            # requests.post(...)
            #
            # =====================================

            print("=" * 60)
            print("WHATSAPP REMINDER")
            print("To :", user.phone)
            print(message)
            print("=" * 60)

            log.status = "Sent"

            log.sent_at = datetime.utcnow()

            db.session.commit()

            return True

        except Exception as e:

            log.status = "Failed"

            log.error_message = str(e)

            db.session.commit()

            print(e)

            return False


    @staticmethod
    def send_due_today(user, reminder):

        message = f"""
🌸 Sayana Press Reminder

Hello {user.full_name},

Your Sayana Press injection
is due TODAY.

Please do not miss your dose.

Stay protected.
"""

        return WhatsAppService.send_reminder(

            user,

            reminder,

            message,

            "Due Today"

        )


    @staticmethod
    def send_tomorrow(user, reminder):

        message = f"""
🌸 Sayana Press Reminder

Hello {user.full_name},

Your next injection
is due TOMORROW.

Please prepare early.

Thank you.
"""

        return WhatsAppService.send_reminder(

            user,

            reminder,

            message,

            "Tomorrow"

        )


    @staticmethod
    def send_three_days(user, reminder):

        message = f"""
🌸 Sayana Press Reminder

Hello {user.full_name},

Your Sayana Press injection
is due in 3 days.

Please don't miss it.
"""

        return WhatsAppService.send_reminder(

            user,

            reminder,

            message,

            "3 Days Before"

        )


    @staticmethod
    def send_seven_days(user, reminder):

        message = f"""
🌸 Sayana Press Reminder

Hello {user.full_name},

Your next Sayana Press injection
is due in 7 days.

Kindly make preparations.

Stay healthy.
"""

        return WhatsAppService.send_reminder(

            user,

            reminder,

            message,

            "7 Days Before"

        )


    @staticmethod
    def send_missed(user, reminder):

        message = f"""
⚠ Missed Injection

Hello {user.full_name},

Our records show
that your scheduled
Sayana Press injection
has been missed.

Please contact your
healthcare provider
as soon as possible.
"""

        return WhatsAppService.send_reminder(

            user,

            reminder,

            message,

            "Missed Dose"

        )