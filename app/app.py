from flask import Flask
from app.routes import main_bp, trip_bp, auth_bp
from config import Config


def create_app():
    app = Flask(__name__,
                template_folder="templates",
                static_folder="templates/static")
    app.secret_key = Config.SECRET_KEY

    app.register_blueprint(main_bp)
    app.register_blueprint(trip_bp)
    app.register_blueprint(auth_bp)

    return app
