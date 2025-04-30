from flask import Blueprint, request, render_template, redirect, url_for, flash
from app import db
from app.models import db, User, ServiceRequest, Schedule
from werkzeug.security import generate_password_hash

bp = Blueprint('main', __name__)


@bp.route('/')
def home():
    return "Hello from Repair Service!"

# Blueprint route for registering a new user


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        contact = request.form.get('contact')
        address = request.form.get('address')
        role = request.form.get('role')  # 'resident' or 'serviceman'
        password = request.form.get('password')

        if not all([name, contact, address, password, role]):
            flash("Please fill all fields.", "danger")
            return redirect(url_for('main.register'))

        hashed_password = generate_password_hash(password)
        user = User(name=name, contact=contact, address=address,
                    password=hashed_password, role=role)

        db.session.add(user)
        db.session.commit()

        flash("Registered successfully!", "success")
        return redirect(url_for('main.register'))

    return render_template('register.html')


# Blueprint route for requesting a service

@bp.route('/request-service', methods=['GET', 'POST'])
def request_service():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        description = request.form.get('description')
        photo_url = request.form.get('photo_url')

        new_request = ServiceRequest(
            user_id=user_id,
            description=description,
            photo_url=photo_url
        )

        db.session.add(new_request)
        db.session.commit()
        flash("Service request submitted successfully!", "success")
        return redirect(url_for('main.home'))

    return render_template('request_service.html')
