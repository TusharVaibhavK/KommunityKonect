from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'abcd1234'
    app.config.from_object(Config)

    # Initialize the login manager
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models (no need to import User separately if not used here)
    from .models import User  # Only if needed for app context

    # Register blueprint ONCE
    from .routes import bp
    app.register_blueprint(bp)

    return app
