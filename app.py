from flask import Flask, render_template, request, redirect, url_for, session, flash
from user import User
from trip import Trip
from database import DatabaseManager
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Initialize database manager
db = DatabaseManager()

# Populate with sample data if database is empty
db.populate_sample_data()

@app.route('/')
def index():
    """Home page - redirect to login if not authenticated"""
    if 'user_email' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = db.get_user_by_email(email)
        if user and user.password == password:
            session['user_email'] = email
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    """Sign up page"""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if db.get_user_by_email(email):
            flash('Email already exists', 'error')
            return redirect(url_for('sign_up'))
        if not name or not email or not password or not confirm_password:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('sign_up'))
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('sign_up'))
        user =  db.create_user(name, email, password)
        if user:
            flash('Sign up successful!', 'success')
            return redirect(url_for('login'))
    return render_template('sign_up.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.pop('user_email', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """User dashboard showing trips"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user = db.get_user_by_email(session['user_email'])
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('login'))
    
    user_id = db.get_user_id_by_email(session['user_email'])
    trips = db.get_user_trips(user_id)
    
    return render_template('dashboard.html', user=user, trips=trips)

@app.route('/add_trip', methods=['GET', 'POST'])
def add_trip():
    """Add a new trip"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        trip_type = request.form['type']
        
        # Create new trip
        new_trip = Trip(city, state, country, start_date, end_date, trip_type)
        
        # Add to user's trips
        user_id = db.get_user_id_by_email(session['user_email'])
        db.create_trip(user_id, city, state, country, start_date, end_date, trip_type)
        
        flash('Trip added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_trip.html')

@app.route('/edit_trip/<int:trip_index>', methods=['GET', 'POST'])
def edit_trip(trip_index):
    """Edit an existing trip"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user = db.get_user_by_email(session['user_email'])
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('login'))
    
    user_id = db.get_user_id_by_email(session['user_email'])
    trips = db.get_user_trips(user_id)
    
    if trip_index >= len(trips):
        flash('Trip not found', 'error')
        return redirect(url_for('dashboard'))
    
    trip = db.get_trip_by_id(trips[trip_index].id)
    
    if request.method == 'POST':
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        trip_type = request.form['type']
        db.update_trip(trip.id, city=city, state=state, country=country, start_date=start_date, end_date=end_date, type=trip_type)
        flash('Trip updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_trip.html', trip=trip, trip_index=trip_index)

@app.route('/delete_trip/<int:trip_index>')
def delete_trip(trip_index):
    """Delete a trip"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user = db.get_user_by_email(session['user_email'])
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('login'))
    
    user_id = db.get_user_id_by_email(session['user_email'])
    trips = db.get_user_trips(user_id)
    
    if trip_index >= len(trips):
        flash('Trip not found', 'error')
    else:
        trip = db.get_trip_by_id(trips[trip_index].id)
        db.delete_trip(trip.id)
        flash('Trip deleted successfully!', 'success')
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
