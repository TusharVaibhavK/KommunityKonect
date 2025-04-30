from flask import Blueprint, request, render_template, redirect, url_for, flash, abort
from app.models import db, User, ServiceRequest, Schedule
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime

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

            # Redirect based on role
            next_page = request.args.get('next')
            if not next_page:
                if user.role == 'serviceman':
                    next_page = url_for('main.service_requests')
                else:
                    next_page = url_for('main.profile')
            return redirect(next_page)

        flash('Invalid email or password', 'danger')

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


# Blueprint route for user profile

@bp.route('/profile')
@login_required  # Ensure that the user is logged in
def profile():
    return render_template('profile.html', user=current_user)


# Blueprint route for viewing all service requests for serviceman

@bp.route('/service-requests')
@login_required
def service_requests():
    if current_user.role != 'serviceman':
        abort(403)

    # Get all pending requests that aren't already scheduled
    pending_requests = ServiceRequest.query.filter_by(
        status='pending'
    ).outerjoin(
        Schedule
    ).filter(
        Schedule.id.is_(None)
    ).all()

    return render_template('service_requests.html', requests=pending_requests)

# Blueprint route for viewing all scheduled service requests for serviceman


@bp.route('/schedule-request/<int:request_id>', methods=['GET', 'POST'])
def schedule_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)

    # Get the current time
    now = datetime.now()

    return render_template('schedule_request.html', request=service_request, now=now)

# blueprint route for calendar view for serviceman


@bp.route('/calendar')
@login_required
def calendar():
    if current_user.role != 'serviceman':
        abort(403)

    # Get all scheduled requests for the serviceman
    scheduled_requests = Schedule.query.filter_by(
        serviceman_id=current_user.id).all()

    return render_template('main/calendar.html', schedules=scheduled_requests)


# Blueprint for debuging routes

@bp.route('/debug/relationships')
def debug_relationships():
    # Create test data if none exists
    if not User.query.first():
        user = User(name="Test User", contact="test@example.com",
                    address="123 St", password=generate_password_hash("test"), role="resident")
        db.session.add(user)
        db.session.commit()

        request = ServiceRequest(
            user_id=user.id,
            service_type="debug",
            description="Test relationship"
        )
        db.session.add(request)
        db.session.commit()

    # Test relationships
    user = User.query.first()
    request = ServiceRequest.query.first()

    return {
        'user_to_requests': bool(user.service_requests),
        'request_to_user': bool(request.user),
        'user': user.name,
        'request': request.id
    }


# # Blueprint route for calander


# @bp.route('/calendar')
# @login_required
# def calendar():
#     if current_user.role != 'serviceman':
#         abort(403)

#     # Get all scheduled requests for the serviceman
#     scheduled_requests = Schedule.query.filter_by(
#         serviceman_id=current_user.id).all()

#     return render_template('calendar.html', schedules=scheduled_requests)


@bp.route('/test-user')
def test_user():
    from app.models import User  # Test import
    users = User.query.all()
    return str([u.name for u in users])


@bp.route('/test-db')
def test_db():
    try:
        from app.models import User
        test_user = User(
            name="Test User",
            contact="test@example.com",
            address="123 Test St",
            password="temp_password",  # Will be hashed
            role="resident"
        )
        test_user.set_password("temp_password")
        db.session.add(test_user)
        db.session.commit()
        return "Database operations successful! Created test user."
    except Exception as e:
        return f"Database error: {str(e)}", 500
