from .routes import main_bp
from .trips import trip_bp
from .auth import auth_bp
from .excel_synchronizer import synchronizer_bp

__all__ = ['main_bp', 'trip_bp', 'auth_bp', 'synchronizer_bp']
