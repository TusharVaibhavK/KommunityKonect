from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models import db, User, ServiceRequest, Schedule
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required

bp = Blueprint('main', __name__)


@bp.route('/')
def home():
    return render_template('home.html')

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


# Blueprint route for logging in a user

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        contact = request.form.get('contact')
        password = request.form.get('password')
        user = User.query.filter_by(contact=contact).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next') or url_for('main.home')
            return redirect(next_page or url_for('main.home'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('main.home'))


# Blueprint route for requesting a service

@bp.route('/request-service', methods=['GET', 'POST'])
# @login_required
def request_service():
    if request.method == 'POST':
        try:
            new_request = ServiceRequest(
                user_id=current_user.id,  # Get the current user's ID
                description=request.form.get('description'),
                service_type=request.form.get(
                    'service_type', 'general'),  # Add default
                # Explicit None if empty
                photo_url=request.form.get('photo_url', None)
            )
            db.session.add(new_request)
            db.session.commit()
            flash("Request submitted!", "success")
            return redirect(url_for('main.home'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('main.request_service'))

    return render_template('request_service.html')

# route for users


@bp.route('/users')
def list_users():
    users = User.query.order_by(User.id).all()  # Get all users sorted by ID
    return render_template('users.html', users=users)


@bp.route('/debug/session')
def debug_session():
    return {
        'is_authenticated': current_user.is_authenticated,
        'user_id': current_user.get_id() if current_user.is_authenticated else None,
        'cookies': dict(request.cookies)
    }


@bp.route('/debug/users')
def debug_users():
    return {'users': [{'id': u.id, 'name': u.name} for u in User.query.all()]}
