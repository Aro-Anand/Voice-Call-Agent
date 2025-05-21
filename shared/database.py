# shared/database.py
import os
import json
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float
from dotenv import load_dotenv

load_dotenv()

# Initialize SQLAlchemy
db = SQLAlchemy()

class CallRecord(db.Model):
    """Model for storing call records"""
    __tablename__ = 'call_records'
    
    id = Column(Integer, primary_key=True)
    room_name = Column(String(50), unique=True, nullable=False)
    dispatch_id = Column(String(100), unique=True, nullable=True)
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_email = Column(String(100), nullable=True)
    customer_query = Column(Text, nullable=True)
    status = Column(String(20), default='pending')  # pending, connected, failed, completed
    call_start = Column(DateTime, nullable=True)
    call_end = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)  # in seconds
    transcript = Column(Text, nullable=True)
    metadata = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<CallRecord {self.id}: {self.customer_name} - {self.status}>'
    
    def to_dict(self):
        """Convert record to dictionary"""
        return {
            'id': self.id,
            'room_name': self.room_name,
            'dispatch_id': self.dispatch_id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'customer_email': self.customer_email,
            'customer_query': self.customer_query,
            'status': self.status,
            'call_start': self.call_start.isoformat() if self.call_start else None,
            'call_end': self.call_end.isoformat() if self.call_end else None,
            'duration': self.duration,
            'transcript': self.transcript,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

class AdminUser(db.Model):
    """Model for admin users"""
    __tablename__ = 'admin_users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f'<AdminUser {self.username}>'

def init_db(app):
    """Initialize the database with the app context"""
    # Configure SQLite database
    db_path = os.getenv('DB_PATH', 'db/calls.sqlite')
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the db with the app
    db.init_app(app)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        
    return db