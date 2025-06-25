from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from urllib.parse import quote_plus

app = Flask(__name__)
app.secret_key = '0a9ffaab9735eb930342c62441cfd01179a57707f7728117'
bcrypt = Bcrypt(app)

# MongoDB Atlas credentials (encoded safely)
username = quote_plus("anshyadav1330")
password = quote_plus("ansh@1234")
mongo_uri = f"mongodb+srv://{username}:{password}@cluster0.sv4hmbu.mongodb.net/?retryWrites=true&w=majority"

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client['ANALYZER']
users_collection = db['MEDCO']

@app.route('/')
def home():
    return redirect(url_for('signin'))

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

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
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

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
    app.run(debug=True)
