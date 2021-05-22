""" Main app """

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth.login"
login.login_message_category = "alert-info"


def create_app(config_class=Config):
    """ Builder for app"""

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from app.auth import bp as auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    from app.errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    from app.wine import bp as wine_bp

    app.register_blueprint(wine_bp, url_prefix="/wine")

    return app


from app import models
