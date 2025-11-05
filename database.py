import sqlite3
import os
from contextlib import contextmanager
from user import User
from trip import Trip

class DatabaseManager:
    """
    SQLite database manager for Tourley application.
    Handles all database operations for users and trips.
    """
    
    def __init__(self, db_path="tourley.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        Automatically handles connection cleanup.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """
        Initialize the database with required tables.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create trips table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    city TEXT NOT NULL,
                    state TEXT NOT NULL,
                    country TEXT NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_trips_user_id ON trips(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
            
            conn.commit()
    
    # User operations
    def create_user(self, name, email, password):
        """
        Create a new user in the database.
        
        Args:
            name (str): User's name
            email (str): User's email
            password (str): User's password
            
        Returns:
            int: User ID if successful, None if failed
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (name, email, password)
                    VALUES (?, ?, ?)
                ''', (name, email, password))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None  # Email already exists
    
    def get_user_by_email(self, email):
        """
        Get user by email address.
        
        Args:
            email (str): User's email
            
        Returns:
            User object or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            
            if row:
                return User(
                    name=row['name'],
                    email=row['email'],
                    password=row['password']
                )
            return None
    
    def get_user_by_id(self, user_id):
        """
        Get user by ID.
        
        Args:
            user_id (int): User's ID
            
        Returns:
            User object or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            
            if row:
                return User(
                    name=row['name'],
                    email=row['email'],
                    password=row['password']
                )
            return None
    
    def update_user(self, user_id, name=None, email=None, password=None):
        """
        Update user information.
        
        Args:
            user_id (int): User's ID
            name (str, optional): New name
            email (str, optional): New email
            password (str, optional): New password
        """
        updates = []
        params = []
        
        if name:
            updates.append('name = ?')
            params.append(name)
        if email:
            updates.append('email = ?')
            params.append(email)
        if password:
            updates.append('password = ?')
            params.append(password)
        
        if updates:
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
    
    def delete_user(self, user_id):
        """
        Delete a user and all their trips.
        
        Args:
            user_id (int): User's ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
    
    # Trip operations
    def create_trip(self, user_id, city, state, country, start_date, end_date, trip_type):
        """
        Create a new trip for a user.
        
        Args:
            user_id (int): User's ID
            city (str): Trip city
            state (str): Trip state/province
            country (str): Trip country
            start_date (str): Start date
            end_date (str): End date
            trip_type (str): Type of trip
            
        Returns:
            int: Trip ID if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trips (user_id, city, state, country, start_date, end_date, type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, city, state, country, start_date, end_date, trip_type))
            conn.commit()
            return cursor.lastrowid
    
    def get_user_trips(self, user_id):
        """
        Get all trips for a specific user.
        
        Args:
            user_id (int): User's ID
            
        Returns:
            list: List of Trip objects
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM trips WHERE user_id = ? ORDER BY created_at DESC
            ''', (user_id,))
            rows = cursor.fetchall()
            
            trips = []
            for row in rows:
                trip = Trip(
                    city=row['city'],
                    state=row['state'],
                    country=row['country'],
                    start_date=row['start_date'],
                    end_date=row['end_date'],
                    type=row['type']
                )
                trip.id = row['id']  # Add database ID
                trips.append(trip)
            
            return trips
    
    def get_trip_by_id(self, trip_id):
        """
        Get a specific trip by ID.
        
        Args:
            trip_id (int): Trip's ID
            
        Returns:
            Trip object or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM trips WHERE id = ?', (trip_id,))
            row = cursor.fetchone()
            
            if row:
                trip = Trip(
                    city=row['city'],
                    state=row['state'],
                    country=row['country'],
                    start_date=row['start_date'],
                    end_date=row['end_date'],
                    type=row['type']
                )
                trip.id = row['id']
                return trip
            return None
    
    def update_trip(self, trip_id, city=None, state=None, country=None, 
                   start_date=None, end_date=None, trip_type=None):
        """
        Update trip information.
        
        Args:
            trip_id (int): Trip's ID
            city (str, optional): New city
            state (str, optional): New state
            country (str, optional): New country
            start_date (str, optional): New start date
            end_date (str, optional): New end date
            trip_type (str, optional): New trip type
        """
        updates = []
        params = []
        
        if city:
            updates.append('city = ?')
            params.append(city)
        if state:
            updates.append('state = ?')
            params.append(state)
        if country:
            updates.append('country = ?')
            params.append(country)
        if start_date:
            updates.append('start_date = ?')
            params.append(start_date)
        if end_date:
            updates.append('end_date = ?')
            params.append(end_date)
        if trip_type:
            updates.append('type = ?')
            params.append(trip_type)
        
        if updates:
            params.append(trip_id)
            query = f"UPDATE trips SET {', '.join(updates)} WHERE id = ?"
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
    
    def delete_trip(self, trip_id):
        """
        Delete a trip.
        
        Args:
            trip_id (int): Trip's ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM trips WHERE id = ?', (trip_id,))
            conn.commit()
    
    def get_user_id_by_email(self, email):
        """
        Get user ID by email address.
        
        Args:
            email (str): User's email
            
        Returns:
            int: User ID or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            return row['id'] if row else None
    
    def populate_sample_data(self):
        """
        Populate the database with sample data for testing.
        """
        # Create sample users
        will_id = self.create_user("Will Cox", "will@gmail.com", "password")
        admin_id = self.create_user("Admin User", "admin@example.com", "admin123")
        
        if will_id:
            # Add sample trips for Will Cox
            self.create_trip(will_id, "Dallas", "Texas", "USA", "2024-06-01", "2024-06-07", "business")
            self.create_trip(will_id, "Paris", "Île-de-France", "France", "2024-07-15", "2024-07-22", "leisure")
        
        if admin_id:
            # Add sample trips for Admin User
            self.create_trip(admin_id, "New York", "New York", "USA", "2024-05-20", "2024-05-25", "business")


# Example usage and testing
if __name__ == "__main__":
    # Initialize database manager
    db = DatabaseManager()
    
    # Populate with sample data
    print("🗄️  Populating database with sample data...")
    db.populate_sample_data()
    
    # Test user operations
    print("\n👤 Testing user operations...")
    user = db.get_user_by_email("will@gmail.com")
    if user:
        print(f"Found user: {user.name} ({user.email})")
        user_id = db.get_user_id_by_email("will@gmail.com")
        print(f"User ID: {user_id}")
    
    # Test trip operations
    print("\n✈️  Testing trip operations...")
    if user:
        trips = db.get_user_trips(user_id)
        print(f"User has {len(trips)} trips:")
        for trip in trips:
            print(f"  - {trip}")
    
    print("\n✅ Database integration test completed!")
