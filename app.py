from flask import Flask, jsonify, request, render_template
from flask_cors import CORS  # You'll need to install this: pip install flask-cors
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from repair_service_platform.config import Config  # Updated import path
from repair_service_platform.app.models import db, User  # Updated import path
from repair_service_platform.app.routes import bp as main_bp  # Updated import path
from repair_service_platform.app.extentions import db, migrate, login_manager  # Updated import path
from repair_service_platform.app import create_app  # Updated import path

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

# Add API routes for your React app
@app.route('/api/data', methods=['GET'])
def get_data():
    # Replace this with your actual data
    data = {
        "message": "Hello from Flask!",
        "items": ["item1", "item2", "item3"]
    }
    return jsonify(data)

@app.route('/api/submit', methods=['POST'])
def submit_data():
    data = request.json
    # Process the data received from React
    # ...
    return jsonify({"status": "success", "message": "Data received"})

if __name__ == '__main__':
    app.run(debug=True)
