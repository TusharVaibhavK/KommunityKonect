from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(120), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20))  # "resident" or "serviceman"
    is_active = db.Column(db.Boolean, default=True)

    service_requests = db.relationship(
        'ServiceRequest', backref='user', lazy=True)
    schedules = db.relationship('Schedule', backref='serviceman', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class ServiceRequest(db.Model):
    __tablename__ = 'service_request'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    service_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    photo_url = db.Column(db.String(500), nullable=True)


class Schedule(db.Model):
    __tablename__ = 'schedule'

    id = db.Column(db.Integer, primary_key=True)
    serviceman_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'))
    scheduled_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="scheduled")


class MarketPrice(db.Model):
    __tablename__ = 'market_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # plumbing, electrical, etc.
    category = db.Column(db.String(100))  # Tap & mixer, Basin & sink, etc.
    service_name = db.Column(db.String(200), nullable=False)
    market_rate = db.Column(db.Float, default=0.0)
    rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.String(20))
    options_count = db.Column(db.Integer, default=0)
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    is_placeholder = db.Column(db.Boolean, default=False)
    
    # New fields for enhanced scraping
    is_main_service = db.Column(db.Boolean, default=False)
    variant_name = db.Column(db.String(100))
    positive_count = db.Column(db.Integer)  # Count of positive reviews
    negative_count = db.Column(db.Integer)  # Count of negative reviews
    neutral_count = db.Column(db.Integer)   # Count of neutral reviews
    notes = db.Column(db.Text)  # For storing additional details like review contexts
    
    def __repr__(self):
        return f'<MarketPrice {self.service_name} at {self.market_rate}>'

