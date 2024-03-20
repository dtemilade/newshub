# Import necessary libraries
from newsapi import NewsApiClient   
from datetime import datetime, timedelta
from flask_login import current_user, login_required, login_user, logout_user, LoginManager, UserMixin
from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from twilio.rest import Client
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
import random

# Initialize Flask application
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///myapp.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'temi@1992')

# Initialize database
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# Define the endpoint for fetching news from the NewsAPI
NEWS_API_ENDPOINT = 'https://newsapi.org/v2/top-headlines'

# Define the User model for database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    birthdate = db.Column(db.Date, nullable=True)
    address = db.Column(db.String(200), nullable=True)
    telephone = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=True)

# Function to load a user from the database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for the homepage
@app.route('/')
def home():
    return render_template('home.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            login_user(user)
            return redirect(url_for('news'))  # Redirect to news page after successful login
        else:
            flash('Invalid Username or Password')
            return redirect(url_for('login'))

    return render_template('login.html')

# Route for protected content, requires login
@app.route('/protected')
@login_required
def protected_route():
    return f'Hello, {current_user.username}!'

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        email = request.form['email']
        birthdate_str = request.form['birthdate']  # Birthdate as string
        address = request.form['address']
        telephone = request.form['telephone']
        gender = request.form['gender']
        # Validate and process registration
        if not username or not password or not fullname:
            flash('Username, password, and fullname are required.', 'error')
        else:
            # Check if the email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email address already exists. Please use a different email.', 'error')
            else:
                # Convert birthdate string to Python date object
                try:
                    birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Invalid birthdate format. Please use YYYY-MM-DD.', 'error')
                    return redirect(url_for('register'))  # Redirect back to registration page                
                # Hash the password
                hashed_password = generate_password_hash(password)                
                # Create a new user object
                new_user = User(
                    username=username, 
                    password=hashed_password, 
                    fullname=fullname,
                    email=email,
                    birthdate=birthdate,
                    address=address,
                    telephone=telephone,
                    gender=gender
                )
                # Add new user to the database
                db.session.add(new_user)
                try:
                    db.session.commit()
                    flash('Registration successful! Please login to access your account.', 'success')
                    return redirect(url_for('login'))  # Redirect after successful registration
                except IntegrityError:
                    db.session.rollback()  # Rollback the transaction
                    flash('An error occurred during registration. Please try again.', 'error')

    return render_template('register.html')

# Route for fetching and displaying news
@app.route('/news', methods=['GET', 'POST'])
def news():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    try:
        country = request.args.get('country')
        category = request.args.get('category')
        if not country or not category:
            return render_template('news.html', current_user=current_user)
        news_api_keys = {
            'us': '8e87a00915424e79b05acecb9cdc03e8',
            'ng': '3fab37f0129b49cf8f3f922937b81368',
            'za': '42b8de2e960e48be84114e6a321edefe',
            'eg': 'ae8097cbbb1b4a119002c880620e8781',
            'ma': 'bbe102eaae2e4e9e9964943b14cc0f2a',
        }
        NEWS_API_KEY = os.environ.get(news_api_keys.get(country), '8e87a00915424e79b05acecb9cdc03e8')
        
        params = {'country': country, 'apiKey': NEWS_API_KEY, 'category': category}

        response = requests.get(NEWS_API_ENDPOINT, params=params)

        if response.status_code == 200:
            news_data = response.json()
            headlines = news_data['articles']
            return render_template('news.html', headlines=headlines, current_user=current_user)
        else:
            return render_template('error.html')
    except Exception as e:
        return render_template('error.html')

# Function to update session and set session timeout
@app.before_request
def update_session():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)
    session['last_activity'] = datetime.now()

@app.route('/logout')
@login_required
def logout():
    # Remove 'logged_in' from session to log out
    session.pop('logged_in', None)
    # Log out user
    logout_user()
    # Redirect to login page
    return redirect(url_for('login'))

@app.route('/view_users', methods=['GET', 'POST'])
def view_users():
    if request.method == 'POST':
        # Get delete password from form
        del_password = request.form['del_password']
        # Hash correct password
        correct_password_hash = generate_password_hash("admin123")

        if check_password_hash(correct_password_hash, del_password):
            # Fetch all users from database
            users = User.query.all()
            # Display users
            return render_template('view_users.html', users=users)
        else:
            # If password is incorrect, show error message and redirect to view_users
            flash('Access Denied, ADMIN ONLY.', 'error')
            return redirect(url_for('view_users'))

    # If it's a GET request or invalid POST request, render access denied template
    users = []
    return render_template('view_users_access.html')

@app.route('/profile')
@login_required
def profile():
    # Display profile of current user
    users = [current_user]
    return render_template('profile.html', users=users)

@app.route('/update_user/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        # Get updated user details from form
        new_username = request.form['username']
        new_password = request.form['password']
        new_fullname = request.form['fullname']
        new_email = request.form['email']
        new_birthdate_str = request.form['birthdate']
        new_birthdate = datetime.strptime(new_birthdate_str, '%Y-%m-%d').date()
        new_address = request.form['address']
        new_telephone = request.form['telephone']
        new_gender = request.form['gender']
        
        # Update user details if provided
        if new_username:
            user.username = new_username
        if new_password:
            user.password = generate_password_hash(new_password)
        if new_fullname:
            user.fullname = new_fullname
        if new_email:
            user.email = new_email
        if new_birthdate:
            user.birthdate = new_birthdate
        if new_address:
            user.address = new_address
        if new_telephone:
            user.telephone = new_telephone
        if new_gender:
            user.gender = new_gender
            
        # Commit changes to database
        db.session.commit()
        # Flash success message and redirect to profile
        flash('User details updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    # Render update_user template
    return render_template('update_user.html', user=user)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        # Get username, email, and new password from form
        username = request.form['username']
        email = request.form['email']
        new_password = request.form['password']

        # Find user by username and email
        user = User.query.filter_by(username=username, email=email).first()

        if user:
            # Change the password for the user
            user.password = generate_password_hash(new_password)
            # Commit changes to database
            db.session.commit()
            # Flash success message and redirect to login
            flash('Password changed successfully!', 'success')
            return redirect(url_for('login'))
        else:
            # If user not found, show error message and redirect to reset_password
            flash('Invalid username or email.', 'error')
            return redirect(url_for('reset_password'))

    # Render reset_password template
    return render_template('reset_password.html')

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    # Find user by ID
    user = User.query.get(user_id)
    # Delete user from database
    db.session.delete(user)
    # Commit changes to database
    db.session.commit()
    # Flash success message and redirect to view_users
    flash('User deleted successfully!', 'success')
    return redirect(url_for('view_users'))

if __name__ == '__main__':
    with app.app_context():
        # Create necessary tables
        db.create_all()
    # Run the Flask app
    app.run(host='0.0.0.0', port=10000, debug=True)
