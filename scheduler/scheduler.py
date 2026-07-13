"""
scheduler.py

Runs background jobs automatically.

Current Jobs
------------
✓ Reminder Service

Future Jobs
------------
✓ Daily Reports
✓ AI Analytics
✓ Knowledge Base Backup
✓ Database Cleanup
"""

from apscheduler.schedulers.background import BackgroundScheduler

from services.reminder_service import ReminderService


class SchedulerService:

    def __init__(self):

        self.scheduler = BackgroundScheduler()

    # ==========================================
    # START SCHEDULER
    # ==========================================

    def start(self):

        # --------------------------------------
        # Every day at 8:00 AM
        # --------------------------------------

        self.scheduler.add_job(

            func=ReminderService.process_reminders,

            trigger="cron",

            hour=8,

            minute=0,

            id="daily_reminders",

            replace_existing=True

        )

        self.scheduler.start()

        print("=" * 60)
        print("Scheduler Started")
        print("Daily Reminder Job : 08:00 AM")
        print("=" * 60)

    # ==========================================
    # STOP
    # ==========================================

    def stop(self):

        self.scheduler.shutdown()

        print("Scheduler Stopped")