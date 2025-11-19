# database.py - MongoDB database connection and user authentication
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(32).hex())
bcrypt = Bcrypt(app)

# MongoDB Atlas credentials - Load from environment variables
mongodb_username = os.getenv("MONGODB_USERNAME")
mongodb_password = os.getenv("MONGODB_PASSWORD")
mongodb_cluster = os.getenv("MONGODB_CLUSTER", "cluster0.sv4hmbu.mongodb.net")

if mongodb_username and mongodb_password:
    username = quote_plus(mongodb_username)
    password = quote_plus(mongodb_password)
    mongo_uri = f"mongodb+srv://{username}:{password}@{mongodb_cluster}/?retryWrites=true&w=majority"
else:
    mongo_uri = None

# Connect to MongoDB (only if credentials are available)
client = None
db = None
users_collection = None

if mongo_uri:
    try:
        client = MongoClient(mongo_uri)
        db = client['ANALYZER']
        users_collection = db['MEDCO']
    except Exception as e:
        print(f"[❌] MongoDB connection error: {e}")

@app.route('/')
def home():
    return redirect(url_for('signin'))

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if not users_collection:
        flash('Database connection not available. Please configure MongoDB credentials.', 'danger')
        return render_template('signin.html')
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return redirect(url_for('signin'))

        user = users_collection.find_one({'email': email})
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user'] = email
            session['name'] = user.get('name', 'User')
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('signin'))

    return render_template('signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if not users_collection:
        flash('Database connection not available. Please configure MongoDB credentials.', 'danger')
        return render_template('signup.html')
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('signup'))

        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            flash('Email already registered. Please sign in.', 'warning')
            return redirect(url_for('signin'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        users_collection.insert_one({'name': name, 'email': email, 'password': hashed_password})
        flash('Registration successful! You can now sign in.', 'success')
        return redirect(url_for('signin'))

    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return f"Welcome, {session.get('name', 'User')}!"
    return redirect(url_for('signin'))

if __name__ == '__main__':
    # In production, set debug=False
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)
