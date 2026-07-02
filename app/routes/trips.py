from flask import Blueprint, render_template, request, session, redirect, url_for, send_file
from app.services import GoogleSheetReaderService, TripHistoryService, ExportTripsService, InvoiceCalculationService
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


@trip_bp.route('/invoice', methods=['GET'])
def get_invoice():
    if not session:
        return redirect(url_for("auth.login"))
    google_sheet_reader_service = GoogleSheetReaderService()
    trip_history_service = TripHistoryService(google_sheet_reader_service)
    invoice_calculation_service = InvoiceCalculationService(google_sheet_reader_service, trip_history_service)

    start_date_str, end_date_str, date_from, date_to = validate_filters()
    company = session.get("name", "")

    today, year, company, address, mf, date_from, date_to, total_trips, total_price, service_fee, service_fee_tva, fiscal_stamp, profit_margin, final_price_with_tva, final_price_with_tva_words, final_price_without_tva = invoice_calculation_service.get_invoice_results(
        company, date_from, date_to)

    return render_template("invoice.html",
                           today=today,
                           year=year,
                           company=company,
                           address=address,
                           mf=mf,
                           date_from=date_from,
                           date_to=date_to,
                           total_trips=total_trips,
                           total_price=total_price, service_fee=service_fee, service_fee_tva=service_fee_tva,
                           fiscal_stamp=fiscal_stamp,
                           profit_margin=profit_margin,
                           final_price_with_tva=final_price_with_tva,
                           final_price_with_tva_words=final_price_with_tva_words,
                           final_price_without_tva=final_price_without_tva
                           )


@trip_bp.route('/export', methods=['GET'])
def generate_export():
    if not session:
        return redirect(url_for("auth.login"))
    google_sheet_reader_service = GoogleSheetReaderService()
    trip_history_service = TripHistoryService(google_sheet_reader_service)
    export_trip_service = ExportTripsService(trip_history_service)
    start_date_str, end_date_str, date_from, date_to = validate_filters()
    company = session.get("name", "")

    file_path = export_trip_service.export_trips_to_excel(company, date_from, date_to)

    download_file_name = f"Courses_{company}_{date_from}_{date_to}.xlsx"

    return send_file(
        file_path,
        as_attachment=True,
        download_name=download_file_name
    )
