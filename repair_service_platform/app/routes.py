from flask import Blueprint, request, render_template, redirect, url_for, flash, abort, jsonify
from repair_service_platform.app.models import db, User, ServiceRequest, Schedule, MarketPrice
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
from repair_service_platform.app.MarketScraperBot.market_scraper import scrape_urbanclap_prices


bp = Blueprint('main', __name__)

# Existing HTML-based Routes


@bp.route('/test')
def test_route():
    return jsonify({"message": "Blueprint is working"}), 200


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


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            contact = data.get('contact')
            password = data.get('password')
        else:
            contact = request.form.get('contact')
            password = request.form.get('password')
        user = User.query.filter_by(contact=contact).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            flash('Logged in successfully!', 'success')

            # Redirect based on role for HTML requests
            next_page = request.args.get('next')
            if not next_page and not request.is_json:
                if user.role == 'serviceman':
                    next_page = url_for('main.service_requests')
                else:
                    next_page = url_for('main.profile')
                return redirect(next_page)

            # Return JSON response for API calls
            return jsonify({"access_token": "mock-token"}), 200

        if request.is_json:
            return jsonify({"error": "Invalid credentials"}), 401
        flash('Invalid email or password', 'danger')

    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('main.home'))


@bp.route('/request-service', methods=['GET', 'POST'])
# @login_required
def request_service():
    if request.method == 'POST':
        try:
            if request.is_json:
                data = request.get_json()
                new_request = ServiceRequest(
                    user_id=current_user.id,
                    description=data.get('description'),
                    service_type=data.get('service_type', 'general'),
                    photo_url=data.get('photo_url', None)
                )
            else:
                new_request = ServiceRequest(
                    user_id=current_user.id,
                    description=request.form.get('description'),
                    service_type=request.form.get('service_type', 'general'),
                    photo_url=request.form.get('photo_url', None)
                )
            db.session.add(new_request)
            db.session.commit()
            flash("Request submitted!", "success")
            if request.is_json:
                return jsonify({"message": "Request submitted", "id": new_request.id}), 201
            return redirect(url_for('main.home'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({"error": str(e)}), 400
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('main.request_service'))

    return render_template('request_service.html')


@bp.route('/users')
def list_users():
    users = User.query.order_by(User.id).all()
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


@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@bp.route('/service-requests')
@login_required
def service_requests():
    if current_user.role != 'serviceman':
        abort(403)

    pending_requests = ServiceRequest.query.filter_by(
        status='pending'
    ).outerjoin(
        Schedule
    ).filter(
        Schedule.id.is_(None)
    ).all()

    return render_template('service_requests.html', requests=pending_requests)


@bp.route('/schedule-request/<int:request_id>', methods=['GET', 'POST'])
def schedule_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    now = datetime.now()
    return render_template('schedule_request.html', request=service_request, now=now)


@bp.route('/calendar')
@login_required
def calendar():
    if current_user.role != 'serviceman':
        abort(403)

    scheduled_requests = Schedule.query.filter_by(
        serviceman_id=current_user.id).all()

    return render_template('main/calendar.html', schedules=scheduled_requests)


@bp.route('/debug/relationships')
def debug_relationships():
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

    user = User.query.first()
    request = ServiceRequest.query.first()

    return {
        'user_to_requests': bool(user.service_requests),
        'request_to_user': bool(request.user),
        'user': user.name,
        'request': request.id
    }


@bp.route('/test-user')
def test_user():
    from app.models import User
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
            password="temp_password",
            role="resident"
        )
        test_user.set_password("temp_password")
        db.session.add(test_user)
        db.session.commit()
        return "Database operations successful! Created test user."
    except Exception as e:
        return f"Database error: {str(e)}", 500



# Market Price Scraper Route
@bp.route('/market-rate')
def market_rate():
    service = request.args.get('service', '')
    result = MarketPrice.query.filter(MarketPrice.service_name.ilike(f"%{service}%")).order_by(MarketPrice.scraped_at.desc()).first()
    if result:
        return jsonify({
            "service": service,
            "avg_price": result.avg_price,
            "scraped_at": result.scraped_at.isoformat()
        })
    else:
        return jsonify({"error": "No data found"}), 404
# @bp.route('/api/market-rate/<int:id>')
# def market_rate_by_id(id):
#     result = MarketPrice.query.get(id)
#     if result:
#         return jsonify({
#             "service": result.service_name,
#             "avg_price": result.avg_price,
#             "scraped_at": result.scraped_at.isoformat()
#         })
#     else:
#         return jsonify({"error": "No data found"}), 404

# New RESTful API Endpoints


@bp.route('/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    contact = data.get('contact')
    password = data.get('password')
    user = User.query.filter_by(contact=contact).first()

    if user and user.check_password(password):
        login_user(user, remember=True)
        return jsonify({"access_token": "mock-token"}), 200
    return jsonify({"error": "Invalid credentials"}), 401


@bp.route('/auth/register', methods=['POST'])
def api_register():
    data = request.get_json()
    name = data.get('name')
    contact = data.get('contact')
    address = data.get('address')
    role = data.get('role')
    password = data.get('password')

    if not all([name, contact, address, password, role]):
        return jsonify({"error": "Please fill all fields"}), 400

    if User.query.filter_by(contact=contact).first():
        return jsonify({"error": "Contact already exists"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(name=name, contact=contact, address=address,
                    password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    return jsonify({"access_token": "mock-token"}), 201


@bp.route('/auth/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({"message": "Logged out"}), 200


@bp.route('/requests', methods=['GET'])
@login_required
def api_get_requests():
    requests = ServiceRequest.query.all()
    return jsonify([{
        'id': r.id,
        'user_id': r.user_id,
        'description': r.description,
        'service_type': r.service_type,
        'status': r.status,
        'photo_url': r.photo_url
    } for r in requests]), 200


@bp.route('/requests/<int:id>', methods=['GET'])
@login_required
def api_get_request(id):
    request = ServiceRequest.query.get_or_404(id)
    return jsonify({
        'id': request.id,
        'user_id': request.user_id,
        'description': request.description,
        'service_type': request.service_type,
        'status': request.status,
        'photo_url': request.photo_url
    }), 200


@bp.route('/requests', methods=['POST'])
@login_required
def api_create_request():
    data = request.get_json()
    new_request = ServiceRequest(
        user_id=current_user.id,
        description=data.get('description'),
        service_type=data.get('service_type', 'general'),
        photo_url=data.get('photo_url', None)
    )
    db.session.add(new_request)
    db.session.commit()
    return jsonify({
        'id': new_request.id,
        'user_id': new_request.user_id,
        'description': new_request.description,
        'service_type': new_request.service_type,
        'status': new_request.status,
        'photo_url': new_request.photo_url
    }), 201


@bp.route('/requests/<int:id>', methods=['PUT'])
@login_required
def api_update_request(id):
    data = request.get_json()
    request = ServiceRequest.query.get_or_404(id)
    if request.user_id != current_user.id and current_user.role != 'serviceman':
        abort(403)
    request.description = data.get('description', request.description)
    request.service_type = data.get('service_type', request.service_type)
    request.photo_url = data.get('photo_url', request.photo_url)
    db.session.commit()
    return jsonify({
        'id': request.id,
        'user_id': request.user_id,
        'description': request.description,
        'service_type': request.service_type,
        'status': request.status,
        'photo_url': request.photo_url
    }), 200


@bp.route('/requests/<int:id>', methods=['DELETE'])
@login_required
def api_delete_request(id):
    request = ServiceRequest.query.get_or_404(id)
    if request.user_id != current_user.id and current_user.role != 'serviceman':
        abort(403)
    db.session.delete(request)
    db.session.commit()
    return jsonify({"message": "Request deleted"}), 200


@bp.route('/schedule', methods=['GET'])
@login_required
def api_get_schedules():
    schedules = Schedule.query.filter_by(serviceman_id=current_user.id).all()
    return jsonify([{
        'id': s.id,
        'request_id': s.request_id,
        'serviceman_id': s.serviceman_id,
        'date': s.date.isoformat(),
        'time': s.time.isoformat()
    } for s in schedules]), 200


@bp.route('/schedule', methods=['POST'])
@login_required
def api_create_schedule():
    data = request.get_json()
    new_schedule = Schedule(
        request_id=data.get('request_id'),
        serviceman_id=current_user.id,
        date=data.get('date'),
        time=data.get('time')
    )
    db.session.add(new_schedule)
    db.session.commit()
    return jsonify({
        'id': new_schedule.id,
        'request_id': new_schedule.request_id,
        'serviceman_id': new_schedule.serviceman_id,
        'date': new_schedule.date.isoformat(),
        'time': new_schedule.time.isoformat()
    }), 201


@bp.route('/users', methods=['GET'])
@login_required
def api_get_users():
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'name': u.name,
        'contact': u.contact,
        'address': u.address,
        'role': u.role
    } for u in users]), 200


@bp.route('/')
def home():
    return render_template('home.html')
