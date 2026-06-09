from flask import Blueprint, render_template, request, session, redirect, url_for
from app.services import AuthService, GoogleSheetReaderService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if "account" in session:
        return redirect(url_for("trip.get_dashboard"))

    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        google_sheet_reader_service = GoogleSheetReaderService()
        auth_service = AuthService(google_sheet_reader_service)
        account = auth_service.login(email, password)
        if account is None:
            error = "Email ou mot de passe incorrect"
            return render_template("login.html", error=error)

        session["account"] = account.login
        session["name"] = account.name
        session["type"] = account.type
        if account.type == "DRIVER":
            session["taxi_number"] = account.taxi_number
        return redirect(url_for("trip.get_dashboard"))

    return render_template("login.html")

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop("account", None)
    session.pop("name", None)
    session.clear()
    return redirect(url_for("auth.login"))
