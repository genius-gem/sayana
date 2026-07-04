from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from models.user import User
from config.database import db


auth_bp = Blueprint(
    "auth",
    __name__
)


# ==========================
# LOGIN
# ==========================

@auth_bp.route(
    "/",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email"
        )

        password = request.form.get(
            "password"
        )

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:

            flash(
                "Account not found.",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        if not check_password_hash(
            user.password,
            password
        ):

            flash(
                "Invalid password.",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        flash(
            "Login successful.",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "auth/login.html"
    )


# ==========================
# REGISTER
# ==========================

@auth_bp.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name"
        )

        email = request.form.get(
            "email"
        )

        password = request.form.get(
            "password"
        )

        existing_user = (
            User.query.filter_by(
                email=email
            ).first()
        )

        if existing_user:

            flash(
                "Email already exists.",
                "danger"
            )

            return redirect(
                url_for("auth.register")
            )

        hashed_password = (
            generate_password_hash(
                password
            )
        )

        user = User(

            full_name=full_name,

            email=email,

            password=hashed_password

        )

        db.session.add(user)

        db.session.commit()

        flash(
            "Registration successful.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "auth/register.html"
    )


# ==========================
# LOGOUT
# ==========================

@auth_bp.route("/logout")
def logout():

    flash(
        "Logged out successfully.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )