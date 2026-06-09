from datetime import datetime


def safe_date_parser(value):
    try:
        if not value:
            return None
        return datetime.strptime(value, "%d/%m/%Y")
    except ValueError:
        return None
