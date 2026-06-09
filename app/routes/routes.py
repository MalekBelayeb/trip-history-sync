from flask import Blueprint, jsonify, redirect, url_for

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def default():
    return redirect(url_for("trip.get_dashboard"))

@main_bp.route('/health')
def health():
    return jsonify({'results': "OK"})
