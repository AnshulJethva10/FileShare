"""
Authentication routes for the File Sharing Application
"""
from flask import Blueprint, request, render_template_string, redirect, url_for, flash, session, current_app
from models import UserModel
from auth_templates import LOGIN_TEMPLATE, SIGNUP_TEMPLATE

# Create blueprint
auth = Blueprint('auth', __name__)

# Initialize user model
user_model = UserModel()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = user_model.authenticate_user(username, password)
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            
            # Ensure user has PQ keys if KEM is enabled
            if hasattr(current_app, 'key_mgmt') and current_app.key_mgmt:
                try:
                    current_app.key_mgmt.ensure_user_keys(user[0], password)
                except Exception as e:
                    print(f"⚠️  Failed to ensure PQ keys for user {user[0]}: {e}")
            
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template_string(LOGIN_TEMPLATE)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template_string(SIGNUP_TEMPLATE)
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template_string(SIGNUP_TEMPLATE)
        
        if user_model.user_exists(username=username):
            flash('Username already exists', 'error')
            return render_template_string(SIGNUP_TEMPLATE)
        
        if user_model.user_exists(email=email):
            flash('Email already exists', 'error')
            return render_template_string(SIGNUP_TEMPLATE)
        
        # Create user
        user_id = user_model.create_user(username, email, password)
        if user_id:
            # Generate PQ keys for new user if KEM is enabled
            if hasattr(current_app, 'key_mgmt') and current_app.key_mgmt:
                try:
                    current_app.key_mgmt.ensure_user_keys(user_id, password)
                    print(f"✅ Generated PQ keys for new user {user_id}")
                except Exception as e:
                    print(f"⚠️  Failed to generate PQ keys for new user: {e}")
            
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Error creating account', 'error')
    
    return render_template_string(SIGNUP_TEMPLATE)

@auth.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))

def login_required(f):
    """Decorator to require login for certain routes"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
