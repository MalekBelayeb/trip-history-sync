from flask import Blueprint, render_template, request, session, redirect, url_for
from app.services import GoogleSheetReaderService, TripHistoryService
from datetime import datetime, date

trip_bp = Blueprint('trip', __name__)


def validate_filters():
    import calendar
    today = date.today()
    default_debut = today.replace(day=1).strftime("%Y-%m-%d")
    default_fin = today.replace(day=calendar.monthrange(today.year, today.month)[1]).strftime("%Y-%m-%d")

    start_date_str = request.args.get("start_date", default_debut)
    end_date_str = request.args.get("end_date", default_fin)
    date_from, date_to = None, None
    if start_date_str:
        try:
            date_from = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass
    if end_date_str:
        try:
            date_to = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass
    return start_date_str, end_date_str, date_from, date_to


@trip_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    if not session:
        return redirect(url_for("auth.login"))

    start_date_str, end_date_str, date_from, date_to = validate_filters()
    company = session.get("name", "")
    account_type = session.get("type", "")
    taxi_number = session.get("taxi_number", None)

    google_sheet_reader_service = GoogleSheetReaderService()
    trip_history_service = TripHistoryService(google_sheet_reader_service)
    sheet_name = ""

    if account_type == "DRIVER":
        sheet_name = taxi_number
    if account_type == "COMPANY":
        sheet_name = company

    trips_by_date_list, total_trips, total_price, total_passengers = trip_history_service.get_daily_trips(
        sheet_name,
        date_from,
        date_to,
    )

    return render_template("dashboard.html",
                           company=company,
                           daily_trips=trips_by_date_list,
                           total_price=total_price,
                           total_passengers=total_passengers,
                           total_trips=total_trips,
                           start_date=start_date_str,
                           end_date=end_date_str,
                           account_type=account_type
                           )
