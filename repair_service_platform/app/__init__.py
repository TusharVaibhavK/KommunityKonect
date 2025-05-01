from flask import Flask
from flask_cors import CORS
from app.extensions import db, migrate, login_manager
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    
    # Configure the app
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Set up user_loader
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)