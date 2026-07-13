"""
email_service.py

Handles sending reminder emails
and recording the delivery status.
"""

from datetime import datetime

from flask import current_app
from flask_mail import Message

from config.database import db
from config.mail import mail

from models.reminder_log import ReminderLog


class EmailService:

    @staticmethod
    def send_reminder(
        user,
        reminder,
        subject,
        body,
        reminder_type="General Reminder"
    ):
        """
        Send reminder email and log the result.
        """

        log = ReminderLog(

            user_id=user.id,

            reminder_id=reminder.id,

            channel="Email",

            reminder_type=reminder_type,

            status="Pending",

            message=body

        )

        db.session.add(log)
        db.session.commit()

        try:

            message = Message(

                subject=subject,

                recipients=[user.email]

            )

            message.body = body

            mail.send(message)

            log.status = "Sent"

            log.sent_at = datetime.utcnow()

            db.session.commit()

            return True

        except Exception as e:

            log.status = "Failed"

            log.error_message = str(e)

            db.session.commit()

            print("EMAIL ERROR:", e)

            return False


    @staticmethod
    def send_due_today(user, reminder):

        subject = "🌸 Sayana Press Reminder"

        body = f"""
Hello {user.full_name},

This is a reminder that your
Sayana Press injection is due TODAY.

Please administer your injection
or visit your healthcare provider.

Missing your injection may reduce
your contraceptive protection.

Stay healthy.

Regards,
SayanaBot
"""

        return EmailService.send_reminder(

            user,

            reminder,

            subject,

            body,

            "Due Today"

        )


    @staticmethod
    def send_tomorrow(user, reminder):

        subject = "🌸 Sayana Press Reminder"

        body = f"""
Hello {user.full_name},

Your next Sayana Press injection
is due TOMORROW.

Please prepare for your appointment
or self-injection.

Thank you.

Regards,
SayanaBot
"""

        return EmailService.send_reminder(

            user,

            reminder,

            subject,

            body,

            "Tomorrow"

        )


    @staticmethod
    def send_three_days(user, reminder):

        subject = "🌸 Sayana Press Reminder"

        body = f"""
Hello {user.full_name},

Your Sayana Press injection
is due in 3 days.

Please don't miss your scheduled dose.

Regards,
SayanaBot
"""

        return EmailService.send_reminder(

            user,

            reminder,

            subject,

            body,

            "3 Days Before"

        )


    @staticmethod
    def send_seven_days(user, reminder):

        subject = "🌸 Sayana Press Reminder"

        body = f"""
Hello {user.full_name},

Your next Sayana Press injection
is due in one week.

We recommend preparing early
to avoid missing your appointment.

Regards,
SayanaBot
"""

        return EmailService.send_reminder(

            user,

            reminder,

            subject,

            body,

            "7 Days Before"

        )


    @staticmethod
    def send_missed(user, reminder):

        subject = "⚠ Missed Sayana Press Injection"

        body = f"""
Hello {user.full_name},

Our records indicate that
your scheduled Sayana Press injection
has been missed.

Please contact your healthcare provider
as soon as possible for advice.

Regards,
SayanaBot
"""

        return EmailService.send_reminder(

            user,

            reminder,

            subject,

            body,

            "Missed Dose"

        )