from sqlalchemy import extract
from collections import defaultdict

from flask import request

from functools import wraps
from datetime import date, timedelta

from chatbot.rebuild_index import rebuild_index


from models.reminder_log import ReminderLog
from models.knowledge import Knowledge
from models.injection_history import InjectionHistory

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    flash,
    request
)

from flask import flash, redirect, url_for

from models.user import User
from models.reminder import Reminder
from models.chat_history import ChatHistory
from models.activity import Activity

from config.database import db


from flask import request
from werkzeug.security import generate_password_hash


import csv
from io import BytesIO

from flask import send_file

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph


from werkzeug.security import generate_password_hash


# ==========================================================
# ADMIN BLUEPRINT
# ==========================================================

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# ==========================================================
# ADMIN LOGIN REQUIRED
# ==========================================================

def admin_required(view):

    @wraps(view)
    def wrapped_view(*args, **kwargs):

        user_id = session.get("user_id")

        if user_id is None:

            flash(
                "Please login first.",
                "warning"
            )

            return redirect(
                url_for("auth.login")
            )

        user = User.query.get(user_id)

        if user is None:

            session.clear()

            flash(
                "Session expired.",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        if not user.is_admin:

            flash(
                "Administrator access required.",
                "danger"
            )

            return redirect(
                url_for("dashboard")
            )

        return view(*args, **kwargs)

    return wrapped_view


# ==========================================================
# ADMIN DASHBOARD
# ==========================================================

@admin_bp.route("/")
@admin_required
def dashboard():

    today = date.today()

    total_users = User.query.filter_by(
        is_admin=False
    ).count()

    active_reminders = Reminder.query.count()

    total_chats = ChatHistory.query.count()

    reminders = Reminder.query.all()

    due_today = 0
    due_soon = 0
    missed_doses = 0
    completed_injections = 0

    for reminder in reminders:

        if reminder.next_injection_date < today:

            missed_doses += 1

        elif reminder.next_injection_date == today:

            due_today += 1

        elif reminder.next_injection_date <= today + timedelta(days=7):

            due_soon += 1

        if reminder.last_injection_date:

            completed_injections += 1

    latest_users = (

        User.query

        .filter_by(is_admin=False)

        .order_by(User.id.desc())

        .limit(10)

        .all()

    )

    recent_activities = (

        Activity.query

        .order_by(Activity.created_at.desc())

        .limit(10)

        .all()

    )

    new_users = (

        User.query

        .filter_by(is_admin=False)

        .count()

    )

    # ==========================================================
# MONTHLY USER REGISTRATION
# ==========================================================

    months = [

        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec"

    ]

    monthly_users = [0] * 12

    users = User.query.filter_by(
        is_admin=False
    ).all()

    for user in users:

        if hasattr(user, "created_at") and user.created_at:

            month = user.created_at.month

            monthly_users[month - 1] += 1


# ==========================================================
# MONTHLY CHATS
# ==========================================================

        monthly_chats = [0] * 12

        all_chats = ChatHistory.query.all()

        for chat in all_chats:

            if chat.created_at:

                month = chat.created_at.month

                monthly_chats[month - 1] += 1


    return render_template(

        "admin/dashboard.html",

        total_users=total_users,

        active_reminders=active_reminders,

        due_today=due_today,

        due_soon=due_soon,

        missed_doses=missed_doses,

        total_chats=total_chats,

        completed_injections=completed_injections,

        latest_users=latest_users,

        recent_activities=recent_activities,

        new_users=new_users,

        months=months,

        monthly_users=monthly_users,

        monthly_chats=monthly_chats,

        completed=completed,

        upcoming=upcoming,

        missed=missed,

        today=today
    )


# ==========================================================
# VIEW USER
# ==========================================================

@admin_bp.route("/users/<int:user_id>")
@admin_required
def view_user(user_id):

    user = User.query.get_or_404(user_id)

    reminder = Reminder.query.filter_by(
        user_id=user.id
    ).first()

    chats = (

        ChatHistory.query

        .filter_by(user_id=user.id)

        .order_by(ChatHistory.created_at.desc())

        .limit(20)

        .all()

    )

    activities = (

        Activity.query

        .filter_by(user_id=user.id)

        .order_by(Activity.created_at.desc())

        .all()

    )

    return render_template(

        "admin/view_user.html",

        user=user,

        reminder=reminder,

        chats=chats,

        activities=activities

    )


# ==========================================================
# USER MANAGEMENT
# ==========================================================

@admin_bp.route("/users")
@admin_required
def users():

    page = request.args.get(

        "page",

        1,

        type=int

    )

    search = request.args.get(

        "search",

        ""

    )

    status = request.args.get(

        "status",

        ""

    )

    query = User.query.filter_by(

        is_admin=False

    )

    # ----------------------------
    # Search
    # ----------------------------

    if search:

        query = query.filter(

            (User.full_name.ilike(f"%{search}%")) |

            (User.email.ilike(f"%{search}%"))

        )

    # ----------------------------
    # Status Filter
    # ----------------------------

    if status == "active":

        query = query.filter(

            User.is_active == True

        )

    elif status == "inactive":

        query = query.filter(

            User.is_active == False

        )

    # ----------------------------
    # Pagination
    # ----------------------------

    users = (

        query

        .order_by(

            User.full_name.asc()

        )

        .paginate(

            page=page,

            per_page=15,

            error_out=False

        )

    )

    return render_template(

        "admin/users.html",

        users=users

    )


# ==========================================================
# EDIT USER
# ==========================================================

@admin_bp.route("/users/<int:user_id>/edit")
@admin_required
def edit_user(user_id):

    user = User.query.get_or_404(user_id)

    reminder = Reminder.query.filter_by(
        user_id=user.id
    ).first()

    return render_template(

        "admin/edit_user.html",

        user=user,

        reminder=reminder

    )


# ==========================================================
# REMINDER MANAGEMENT
# ==========================================================

@admin_bp.route("/reminders")
@admin_required
def reminders():

    reminders = (

        Reminder.query

        .order_by(Reminder.next_injection_date.asc())

        .all()

    )

    return render_template(

        "admin/reminders.html",

        reminders=reminders,

        today=date.today()

    )


# ==========================================================
# CHAT HISTORY
# ==========================================================

@admin_bp.route("/chats")
@admin_required
def chats():

    chats = (

        ChatHistory.query

        .order_by(ChatHistory.created_at.desc())

        .all()

    )

    return render_template(

        "admin/chats.html",

        chats=chats

    )


# ==========================================================
# RESEND REMINDER
# ==========================================================

@admin_bp.route("/reminder-logs/<int:log_id>/resend")
@admin_required
def resend_reminder(log_id):

    log = ReminderLog.query.get_or_404(log_id)

    user = log.user

    reminder = log.reminder

    if log.channel == "Email":

        from services.email_service import EmailService

        EmailService.send_reminder(

            user,

            reminder,

            "Sayana Press Reminder",

            log.message,

            log.reminder_type

        )

    else:

        from services.whatsapp_service import WhatsAppService

        WhatsAppService.send_reminder(

            user,

            reminder,

            log.message,

            log.reminder_type

        )

    flash(

        "Reminder sent successfully.",

        "success"

    )

    return redirect(

        url_for(

            "admin.reminder_logs"

        )

    )


# ==========================================================
# KNOWLEDGE BASE
# ==========================================================

@admin_bp.route("/knowledge")
@admin_required
def knowledge():

    articles = (

        Knowledge.query

        .order_by(
            Knowledge.category.asc(),
            Knowledge.title.asc()
        )

        .all()

    )

    categories = list({

        article.category

        for article in articles

    })

    return render_template(

        "admin/knowledge.html",

        articles=articles,

        categories=categories

    )


# ==========================================================
# ADD ARTICLE
# ==========================================================

@admin_bp.route(
    "/knowledge/add",
    methods=["POST"]
)
@admin_required
def add_article():

    article = Knowledge(

        title=request.form.get("title"),

        category=request.form.get("category"),

        content=request.form.get("content"),

        keywords=request.form.get("keywords")

    )

    db.session.add(article)

    db.session.commit()

    # Automatically rebuild AI index
    rebuild_index()

    flash(
        "Knowledge article added successfully. AI knowledge updated.",
        "success"
    )

    return redirect(
        url_for("admin.knowledge")
    )


# ==========================================================
# REPORTS
# ==========================================================

@admin_bp.route("/reports")
@admin_required
def reports():

    return render_template(
        "admin/reports.html"
    )


# ==========================================================
# EXPORT REPORT (CSV)
# ==========================================================

@admin_bp.route("/export/csv")
@admin_required
def export_csv():

    output = BytesIO()

    text_output = output.write

    import io

    string_buffer = io.StringIO()

    writer = csv.writer(string_buffer)

    writer.writerow([

        "Full Name",

        "Email",

        "Phone",

        "Location",

        "Next Injection",

        "WhatsApp",

        "Email Reminder"

    ])

    users = User.query.filter_by(
        is_admin=False
    ).all()

    for user in users:

        reminder = Reminder.query.filter_by(
            user_id=user.id
        ).first()

        writer.writerow([

            user.full_name,

            user.email,

            user.phone,

            user.location,

            reminder.next_injection_date if reminder else "",

            user.whatsapp_enabled,

            user.email_enabled

        ])

    output.write(
        string_buffer.getvalue().encode("utf-8")
    )

    output.seek(0)

    return send_file(

        output,

        as_attachment=True,

        download_name="sayana_reports.csv",

        mimetype="text/csv"

    )


# ==========================================================
# EXPORT REPORT (PDF)
# ==========================================================

@admin_bp.route("/export/pdf")
@admin_required
def export_pdf():

    buffer = BytesIO()

    document = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(

        Paragraph(

            "<b>Sayana Press Report</b>",

            styles["Title"]

        )

    )

    elements.append(

        Paragraph(

            "Registered Users",

            styles["Heading2"]

        )

    )

    data = [[

        "Name",

        "Email",

        "Phone",

        "Location"

    ]]

    users = User.query.filter_by(
        is_admin=False
    ).all()

    for user in users:

        data.append([

            user.full_name,

            user.email,

            user.phone,

            user.location

        ])

    table = Table(data)

    table.setStyle(

        TableStyle([

            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#7C3AED")),

            ("TEXTCOLOR",(0,0),(-1,0),colors.white),

            ("GRID",(0,0),(-1,-1),1,colors.grey),

            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),

            ("BOTTOMPADDING",(0,0),(-1,0),10),

            ("BACKGROUND",(0,1),(-1,-1),colors.beige)

        ])

    )

    elements.append(table)

    document.build(elements)

    buffer.seek(0)

    return send_file(

        buffer,

        as_attachment=True,

        download_name="sayana_reports.pdf",

        mimetype="application/pdf"

    )


# ==========================================================
# SETTINGS
# ==========================================================

@admin_bp.route("/settings")
@admin_required
def settings():

    return render_template(
        "admin/settings.html"
    )

# ==========================================================
# EDIT USER
# ==========================================================


# ==========================================================
# UPDATE USER
# ==========================================================

@admin_bp.route(
    "/users/<int:user_id>/update",
    methods=["POST"]
)
@admin_required
def update_user(user_id):

    user = User.query.get_or_404(user_id)

    # ----------------------------------
    # Basic Information
    # ----------------------------------

    user.full_name = request.form.get(
        "full_name",
        user.full_name
    ).strip()

    user.email = request.form.get(
        "email",
        user.email
    ).strip()

    user.phone = request.form.get(
        "phone",
        user.phone
    ).strip()

    user.location = request.form.get(
        "location",
        user.location
    ).strip()

    # ----------------------------------
    # Reminder Preferences
    # ----------------------------------

    user.whatsapp_enabled = (
        request.form.get("whatsapp_enabled") == "on"
    )

    user.email_enabled = (
        request.form.get("email_enabled") == "on"
    )

    # ----------------------------------
    # Account Status
    # ----------------------------------

    user.is_active = (
        request.form.get("is_active") == "on"
    )

    db.session.commit()

    flash(
        "User updated successfully.",
        "success"
    )

    return redirect(
        url_for("admin.users")
    )


# ==========================================================
# UPDATE PASSWORD
# ==========================================================

@admin_bp.route(
    "/users/<int:user_id>/reset-password",
    methods=["POST"]
)
@admin_required
def update_password(user_id):

    user = User.query.get_or_404(user_id)

    password = request.form.get("password")

    confirm_password = request.form.get("confirm_password")

    if password != confirm_password:

        flash(

            "Passwords do not match.",

            "danger"

        )

        return redirect(

            url_for(

                "admin.reset_password",

                user_id=user.id

            )

        )

    user.password = generate_password_hash(password)

    db.session.commit()

    flash(

        "Password updated successfully.",

        "success"

    )

    return redirect(

        url_for(

            "admin.users"

        )

    )


# ==========================================================
# DELETE USER (CONFIRMATION PAGE)
# ==========================================================

@admin_bp.route(
    "/users/<int:user_id>/delete"
)
@admin_required
def delete_user(user_id):

    user = User.query.get_or_404(user_id)

    return render_template(

        "admin/delete_user.html",

        user=user

    )


# ==========================================================
# CONFIRM DELETE USER
# ==========================================================

@admin_bp.route(
    "/users/<int:user_id>/delete/confirm",
    methods=["POST"]
)
@admin_required
def confirm_delete_user(user_id):

    user = User.query.get_or_404(user_id)

    if user.is_admin:

        flash(

            "Administrator account cannot be deleted.",

            "danger"

        )

        return redirect(

            url_for(

                "admin.users"

            )

        )

    Reminder.query.filter_by(
        user_id=user.id
    ).delete()

    ChatHistory.query.filter_by(
        user_id=user.id
    ).delete()

    Activity.query.filter_by(
        user_id=user.id
    ).delete()

    ReminderLog.query.filter_by(
        user_id=user.id
    ).delete()

    db.session.delete(user)

    db.session.commit()

    flash(

        "User deleted successfully.",

        "success"

    )

    return redirect(

        url_for(

            "admin.users"

        )

    )


# ==========================================================
# RESET PASSWORD
# ==========================================================

@admin_bp.route(
    "/users/<int:user_id>/reset-password",
    methods=["POST"]
)
@admin_required
def reset_password(user_id):

    user = User.query.get_or_404(user_id)

    user.password = generate_password_hash(
        "Password123"
    )

    db.session.commit()

    flash(
        "Password reset successfully.",
        "success"
    )

    return redirect(
        url_for(
            "admin.view_user",
            user_id=user.id
        )
    )


# ==========================================================
# ENABLE/DISABLE USER
# ==========================================================

@admin_bp.route(
    "/users/<int:user_id>/toggle",
    methods=["POST"]
)
@admin_required
def toggle_user(user_id):

    user = User.query.get_or_404(user_id)

    if user.is_admin:

        flash(
            "Administrator cannot be disabled.",
            "warning"
        )

        return redirect(
            url_for("admin.users")
        )

    user.is_active = not user.is_active

    db.session.commit()

    flash(
        "User status updated.",
        "success"
    )

    return redirect(
        url_for("admin.users")
    )



# ==========================================================
# EDIT ARTICLE
# ==========================================================

@admin_bp.route(
    "/knowledge/edit/<int:article_id>",
    methods=["GET", "POST"]
)
@admin_required
def edit_article(article_id):

    article = Knowledge.query.get_or_404(article_id)

    if request.method == "POST":

        article.title = request.form.get("title")

        article.category = request.form.get("category")

        article.content = request.form.get("content")

        article.keywords = request.form.get("keywords")

        article.is_active = (
            request.form.get("is_active") == "on"
        )

        db.session.commit()

        flash(
            "Knowledge article updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin.knowledge")
        )

    return render_template(

        "admin/edit_article.html",

        article=article

    )


# ==========================================================
# DELETE ARTICLE
# ==========================================================

@admin_bp.route(
    "/knowledge/delete/<int:article_id>"
)
@admin_required
def delete_article(article_id):

    article = Knowledge.query.get_or_404(
        article_id
    )

    db.session.delete(article)

    db.session.commit()

    # Automatically rebuild AI knowledge
    rebuild_index()

    flash(
        "Knowledge article deleted successfully. AI knowledge updated.",
        "success"
    )

    return redirect(
        url_for("admin.knowledge")
    )


# ==========================================================
# REBUILD AI KNOWLEDGE
# ==========================================================

@admin_bp.route(
    "/knowledge/rebuild"
)
@admin_required
def rebuild_vectors():

    rebuild_index()

    flash(

        "AI knowledge base rebuilt successfully.",

        "success"

    )

    return redirect(

        url_for("admin.knowledge")

    )


# ==========================================================
# REMINDER LOGS
# ==========================================================

@admin_bp.route("/reminder-logs")
@admin_required
def reminder_logs():

    page = request.args.get(
        "page",
        1,
        type=int
    )

    search = request.args.get(
        "search",
        ""
    )

    status = request.args.get(
        "status",
        ""
    )

    channel = request.args.get(
        "channel",
        ""
    )

    query = ReminderLog.query

    if search:

        query = query.join(User).filter(

            User.full_name.ilike(

                f"%{search}%"

            )

        )

    if status:

        query = query.filter(

            ReminderLog.status == status

        )

    if channel:

        query = query.filter(

            ReminderLog.channel == channel

        )

    logs = (

        query

        .order_by(

            ReminderLog.created_at.desc()

        )

        .paginate(

            page=page,

            per_page=20,

            error_out=False

        )

    )

    total = ReminderLog.query.count()

    sent = ReminderLog.query.filter_by(
        status="Sent"
    ).count()

    pending = ReminderLog.query.filter_by(
        status="Pending"
    ).count()

    failed = ReminderLog.query.filter_by(
        status="Failed"
    ).count()

    return render_template(

        "admin/reminder_logs.html",

        logs=logs,

        total=total,

        sent=sent,

        pending=pending,

        failed=failed

    )


   # ==========================================================
# INJECTION HISTORY
# ==========================================================

@admin_bp.route("/injections")
@admin_required
def injections():

    page = request.args.get(
        "page",
        1,
        type=int
    )

    injections = (

        InjectionHistory.query

        .order_by(
            InjectionHistory.injection_date.desc()
        )

        .paginate(
            page=page,
            per_page=20,
            error_out=False
        )

    )

    return render_template(

        "admin/injection_history.html",

        injections=injections

    )

# ==========================================================
# USER INJECTION HISTORY
# ==========================================================

@admin_bp.route("/users/<int:user_id>/injections")
@admin_required
def user_injections(user_id):

    user = User.query.get_or_404(user_id)

    injections = (

        InjectionHistory.query

        .filter_by(
            user_id=user.id
        )

        .order_by(
            InjectionHistory.injection_number.asc()
        )

        .all()

    )

    return render_template(

        "admin/user_injections.html",

        user=user,

        injections=injections

    )

# ==========================================================
# ADD INJECTION
# ==========================================================

@admin_bp.route(
    "/users/<int:user_id>/injections/add"
)
@admin_required
def add_injection(user_id):

    user = User.query.get_or_404(user_id)

    return render_template(

        "admin/add_injection.html",

        user=user

    )

# ==========================================================
# SAVE INJECTION
# ==========================================================

@admin_bp.route(
    "/users/<int:user_id>/injections/save",
    methods=["POST"]
)
@admin_required
def save_injection(user_id):

    user = User.query.get_or_404(user_id)

    injection_date = datetime.strptime(

        request.form["injection_date"],

        "%Y-%m-%d"

    ).date()

    next_date = injection_date + timedelta(weeks=13)

    total = InjectionHistory.query.filter_by(
        user_id=user.id
    ).count()

    injection = InjectionHistory(

        user_id=user.id,

        injection_number=total + 1,

        injection_date=injection_date,

        next_injection_date=next_date,

        injection_site=request.form["injection_site"],

        administered_by=request.form["administered_by"],

        status=request.form["status"],

        notes=request.form.get(
            "notes",
            ""
        )

    )

    db.session.add(injection)

    # Update reminder table

    reminder = Reminder.query.filter_by(
        user_id=user.id
    ).first()

    if reminder:

        reminder.last_injection_date = injection_date

        reminder.next_injection_date = next_date

        reminder.reminder_sent = False

    else:

        reminder = Reminder(

            user_id=user.id,

            last_injection_date=injection_date,

            next_injection_date=next_date,

            reminder_sent=False,

            whatsapp_enabled=user.whatsapp_enabled,

            email_enabled=user.email_enabled

        )

        db.session.add(reminder)

    db.session.commit()

    flash(

        "Injection recorded successfully.",

        "success"

    )

    return redirect(

        url_for(

            "admin.user_injections",

            user_id=user.id

        )

    )

    # ==========================================================
# EDIT INJECTION
# ==========================================================

@admin_bp.route(
    "/injections/<int:injection_id>/edit"
)
@admin_required
def edit_injection(injection_id):

    injection = InjectionHistory.query.get_or_404(
        injection_id
    )

    return render_template(

        "admin/edit_injection.html",

        injection=injection

    )

# ==========================================================
# UPDATE INJECTION
# ==========================================================

@admin_bp.route(
    "/injections/<int:injection_id>/update",
    methods=["POST"]
)
@admin_required
def update_injection(injection_id):

    injection = InjectionHistory.query.get_or_404(
        injection_id
    )

    injection_date = datetime.strptime(

        request.form["injection_date"],

        "%Y-%m-%d"

    ).date()

    next_date = injection_date + timedelta(
        weeks=13
    )

    injection.injection_date = injection_date

    injection.next_injection_date = next_date

    injection.injection_site = request.form[
        "injection_site"
    ]

    injection.administered_by = request.form[
        "administered_by"
    ]

    injection.status = request.form[
        "status"
    ]

    injection.notes = request.form.get(
        "notes",
        ""
    )

    reminder = Reminder.query.filter_by(
        user_id=injection.user_id
    ).first()

    if reminder:

        reminder.last_injection_date = injection_date

        reminder.next_injection_date = next_date

    db.session.commit()

    flash(

        "Injection updated successfully.",

        "success"

    )

    return redirect(

        url_for(

            "admin.user_injections",

            user_id=injection.user_id

        )

    )

# ==========================================================
# DELETE INJECTION
# ==========================================================

@admin_bp.route(
    "/injections/<int:injection_id>/delete",
    methods=["POST"]
)
@admin_required
def delete_injection(injection_id):

    injection = InjectionHistory.query.get_or_404(
        injection_id
    )

    user_id = injection.user_id

    db.session.delete(injection)

    db.session.commit()

    flash(

        "Injection deleted successfully.",

        "success"

    )

    return redirect(

        url_for(

            "admin.user_injections",

            user_id=user_id

        )

    )