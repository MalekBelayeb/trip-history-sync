from flask import Blueprint, request, jsonify

from app.services import GoogleSheetReaderService
from app.services.excel_synchronizer_service import ExcelSynchronizerService

synchronizer_bp = Blueprint('synchronizer', __name__)


@synchronizer_bp.route('/company-trips/push-to-drivers')
def synchronize_trips_by_company():
    company = request.args.get('company')

    if not company:
        return jsonify({
            'error': 'company query parameter is required'
        })

    google_sheet_reader_service = GoogleSheetReaderService()
    google_sheet_reader_service = ExcelSynchronizerService(google_sheet_reader_service)
    results = google_sheet_reader_service.synchronize_trips_by_company(company)

    return jsonify({'results': results})


@synchronizer_bp.route('/company-trips/push-to-driver')
def synchronize_trips_by_company_and_driver():
    company = request.args.get('company')
    driver = request.args.get('driver')

    if not driver:
        return jsonify({
            'error': 'driver query parameter is required'
        })

    if not company:
        return jsonify({
            'error': 'company query parameter is required'
        })

    google_sheet_reader_service = GoogleSheetReaderService()
    google_sheet_reader_service = ExcelSynchronizerService(google_sheet_reader_service)
    trip_count = google_sheet_reader_service.synchronize_trips_by_company_and_driver(company, driver)

    return jsonify({'trip_count': trip_count})
