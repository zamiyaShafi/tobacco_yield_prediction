from flask import Flask, request, render_template, redirect, url_for, session, flash
import joblib
import pandas as pd
import numpy as np
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret_key"

# Load the model
model = joblib.load('tobacco.pkl')

# SQLite Database Connection
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash the password for security
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            # Insert the new user into the database
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            return render_template('login.html',msg="Registration Successfull...please login")
        except sqlite3.IntegrityError:
            return render_template('register.html',msg="Username already exists. Please choose a different one.")
        finally:
            conn.close()
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = username  # Store username in session
            return render_template('index.html', msg='Login Successfull')
        else:
            return render_template('login.html', msg='Invalid Username or Password')
    return render_template('login.html', msg=msg)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if 'user' not in session:
        return render_template('login.html',msg="Please Login")
    prediction = ''
    input_values = {}
    if request.method == 'POST':
        try:
            # Capture input values
            input_values['region'] = request.form['region']
            input_values['temperature'] = request.form['temperature']
            input_values['rainfall'] = request.form['rainfall']
            input_values['humidity'] = request.form['humidity']
            input_values['soil_ph'] = request.form['soil_ph']
            input_values['nitrogen'] = request.form['nitrogen']
            input_values['phosphorus'] = request.form['phosphorus']
            input_values['potassium'] = request.form['potassium']
            
            # Convert values to appropriate types for prediction
            region = int(input_values['region'])
            temperature = float(input_values['temperature'])
            rainfall = float(input_values['rainfall'])
            humidity = float(input_values['humidity'])
            soil_ph = float(input_values['soil_ph'])
            nitrogen = float(input_values['nitrogen'])
            phosphorus = float(input_values['phosphorus'])
            potassium = float(input_values['potassium'])
            
            # Create an array with the form data in the correct order
            features = np.array([[region, temperature, rainfall, humidity, soil_ph, nitrogen, phosphorus, potassium]])
            
            # Predict the yield
            prediction = model.predict(features)[0]
        except Exception as e:
            prediction = f"Error: {str(e)}"

    return render_template('services.html', prediction=prediction, input_values=input_values)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
