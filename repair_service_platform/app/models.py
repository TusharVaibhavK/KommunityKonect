from . import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20))  # "resident" or "serviceman"


class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    service_type = db.Column(db.String(50))  # e.g., "sink", "electricity"
    description = db.Column(db.Text)
    # pending, accepted, done
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serviceman_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'))
    scheduled_time = db.Column(db.DateTime)
    # status = db.Column(db.String(20))  # "scheduled", "completed"
