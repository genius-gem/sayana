from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from config.database import db
from models.user import User


auth_bp = Blueprint(
    "auth",
    __name__
)


# ==========================================================
# LOGIN
# ==========================================================

@auth_bp.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        # -----------------------------
        # Validate
        # -----------------------------

        if not email or not password:

            flash(
                "Please enter your email and password.",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        # -----------------------------
        # Find User
        # -----------------------------

        user = User.query.filter_by(
            email=email
        ).first()

        if user is None:

            flash(
                "No account was found with that email address.",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        # -----------------------------
        # Verify Password
        # -----------------------------

        if not check_password_hash(
            user.password,
            password
        ):

            flash(
                "Incorrect password.",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        # -----------------------------
        # Create Session
        # -----------------------------

        session.clear()

        session["user_id"] = user.id
        session["user_name"] = user.full_name
        session["user_email"] = user.email

        flash(
            f"Welcome back, {user.full_name}!",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "auth/login.html"
    )


# ==========================================================
# REGISTER
# ==========================================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        # -----------------------------
        # Validate Required Fields
        # -----------------------------

        if not full_name or not email or not password:

            flash(
                "Please complete all required fields.",
                "danger"
            )

            return redirect(
                url_for("auth.register")
            )

        # -----------------------------
        # Check Existing Email
        # -----------------------------

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "An account with this email already exists.",
                "danger"
            )

            return redirect(
                url_for("auth.register")
            )

        # -----------------------------
        # Create User
        # -----------------------------

        new_user = User(

    full_name=full_name,

    email=email,

    password=generate_password_hash(password),

    phone=phone,

    location=location,

    whatsapp_enabled=True,

    email_enabled=False
)

        db.session.add(new_user)
        db.session.commit()

        flash(
            "Registration successful. Please log in.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "auth/register.html"
    )


# ==========================================================
# LOGOUT
# ==========================================================

@auth_bp.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )