# from . import db
# from datetime import datetime
# from flask_login import UserMixin
# from werkzeug.security import generate_password_hash, check_password_hash


# class User(db.Model, UserMixin):
#     __tablename__ = 'user'  # Explicit table name

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(120), nullable=False)
#     contact = db.Column(db.String(100), nullable=False)
#     address = db.Column(db.String(200), nullable=False)
#     password = db.Column(db.String(200), nullable=False)
#     role = db.Column(db.String(20))  # "resident" or "serviceman"
#     is_active = db.Column(db.Boolean, default=True)
#     is_authenticated = db.Column(db.Boolean, default=True)

#     # Only ONE relationship to ServiceRequest
#     service_requests = db.relationship(
#         'ServiceRequest', back_populates='user', lazy=True)
#     schedules = db.relationship('Schedule', back_populates='serviceman')

#     def get_id(self):
#         return str(self.id)

#     def set_password(self, password):
#         self.password = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password, password)


# class ServiceRequest(db.Model):
#     __tablename__ = 'service_request'

#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     service_type = db.Column(db.String(50))  # e.g., "sink", "electricity"
#     description = db.Column(db.Text)
#     # pending, scheduled, completed
#     status = db.Column(db.String(20), default="pending")
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     photo_url = db.Column(db.String(500), nullable=True)

#     # Relationship to User (matches the one in User class)
#     user = db.relationship('User', back_populates='service_requests')
#     schedule = db.relationship(
#         'Schedule', back_populates='request', uselist=False)


# class Schedule(db.Model):
#     __tablename__ = 'schedule'

#     id = db.Column(db.Integer, primary_key=True)
#     serviceman_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'))
#     scheduled_time = db.Column(db.DateTime)
#     # scheduled, in-progress, completed
#     status = db.Column(db.String(20), default="scheduled")

#     # Relationships
#     serviceman = db.relationship('User', back_populates='schedules')
#     request = db.relationship('ServiceRequest', back_populates='schedule')


from . import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20))  # "resident" or "serviceman"
    is_active = db.Column(db.Boolean, default=True)

    service_requests = db.relationship(
        'ServiceRequest', backref='user', lazy=True)
    schedules = db.relationship('Schedule', backref='serviceman', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class ServiceRequest(db.Model):
    __tablename__ = 'service_request'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    service_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    photo_url = db.Column(db.String(500), nullable=True)


class Schedule(db.Model):
    __tablename__ = 'schedule'

    id = db.Column(db.Integer, primary_key=True)
    serviceman_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'))
    scheduled_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="scheduled")
