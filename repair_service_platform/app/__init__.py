from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from repair_service_platform.config import Config
from repair_service_platform.app.extentions import db, migrate, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize CORS
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    with app.app_context():
        # Import models after db initialization to avoid circular imports
        from repair_service_platform.app.models import User

        # Define user_loader for Flask-Login
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

    # Import and register blueprint after app context is set up
    try:
        from repair_service_platform.app.routes import bp as main_bp
        app.register_blueprint(main_bp, url_prefix='/api')
        print("Blueprint registered successfully")
    except ImportError as e:
        print(f"Failed to import blueprint: {e}")
        raise

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)