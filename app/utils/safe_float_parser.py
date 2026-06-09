def safe_float_parser(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except ValueError:
        return None
