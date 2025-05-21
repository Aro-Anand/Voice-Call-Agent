# web/admin.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from shared.database import db, CallRecord, AdminUser
import os
import logging
import datetime
import json

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = 'admin.login'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    user = AdminUser.query.get(int(user_id))
    if user:
        return User(user.id, user.username)
    return None

def init_admin(app):
    """Initialize admin functionality"""
    login_manager.init_app(app)
    app.register_blueprint(admin_bp)
    
    # Create default admin user if it doesn't exist
    with app.app_context():
        if not AdminUser.query.filter_by(username=os.getenv('ADMIN_USERNAME', 'admin')).first():
            default_admin = AdminUser(
                username=os.getenv('ADMIN_USERNAME', 'admin'),
                password_hash=generate_password_hash(os.getenv('ADMIN_PASSWORD', 'admin'))
            )
            db.session.add(default_admin)
            db.session.commit()
            logger.info("Created default admin user")

# Routes
@admin_bp.route('/')
@login_required
def index():
    """Admin dashboard"""
    # Get basic stats
    total_calls = CallRecord.query.count()
    completed_calls = CallRecord.query.filter_by(status='completed').count()
    failed_calls = CallRecord.query.filter_by(status='failed').count()
    
    # Get recent calls (last 10)
    recent_calls = CallRecord.query.order_by(CallRecord.created_at.desc()).limit(10).all()
    
    return render_template(
        'admin/index.html', 
        total_calls=total_calls,
        completed_calls=completed_calls, 
        failed_calls=failed_calls,
        recent_calls=recent_calls
    )

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = AdminUser.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            # Update last login time
            admin.last_login = datetime.datetime.utcnow()
            db.session.commit()
            
            # Login the user
            user = User(admin.id, admin.username)
            login_user(user)
            logger.info(f"Admin user {username} logged in")
            
            # Redirect to requested page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.index'))
        else:
            flash('Invalid username or password', 'danger')
            logger.warning(f"Failed login attempt for username: {username}")
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    """Admin logout"""
    logout_user()
    return redirect(url_for('admin.login'))

@admin_bp.route('/calls')
@login_required
def calls():
    """List all calls"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Filter options
    status = request.args.get('status')
    search = request.args.get('search')
    
    query = CallRecord.query
    
    # Apply filters
    if status:
        query = query.filter_by(status=status)
    
    if search:
        query = query.filter(
            (CallRecord.customer_name.like(f'%{search}%')) |
            (CallRecord.customer_phone.like(f'%{search}%')) |
            (CallRecord.customer_email.like(f'%{search}%'))
        )
    
    # Get paginated results
    calls = query.order_by(CallRecord.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return render_template('admin/calls.html', calls=calls)

@admin_bp.route('/calls/<int:call_id>')
@login_required
def call_details(call_id):
    """View details of a specific call"""
    call = CallRecord.query.get_or_404(call_id)
    return render_template('admin/call_details.html', call=call)

@admin_bp.route('/api/calls')
@login_required
def api_calls():
    """API endpoint to get call data for AJAX requests"""
    calls = CallRecord.query.order_by(CallRecord.created_at.desc()).all()
    return jsonify([call.to_dict() for call in calls])

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Admin settings page"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        admin = AdminUser.query.get(current_user.id)
        
        if not check_password_hash(admin.password_hash, current_password):
            flash('Current password is incorrect', 'danger')
        elif new_password != confirm_password:
            flash('New passwords do not match', 'danger')
        else:
            admin.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash('Password updated successfully', 'success')
            logger.info(f"Admin user {admin.username} changed password")
    
    return render_template('admin/settings.html')