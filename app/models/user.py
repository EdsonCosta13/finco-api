from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, get_jwt

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'employee', 'manager', 'admin'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with Company is defined in the Company model as 'employees'
    
    def __init__(self, name, email, password, role, company_id=None, is_admin=False):
        self.name = name
        self.email = email
        self.role = role
        self.company_id = company_id
        self.is_admin = is_admin
        self.set_password(password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'company_id': self.company_id,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def is_employee(self):
        """Check if user is an employee"""
        return self.role == 'employee' and self.is_active

    def is_manager(self):
        """Check if user is a manager"""
        return self.role == 'manager' and self.is_active

    @staticmethod
    def employee_required(f):
        """Decorator to require employee role"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            jwt = get_jwt()
            
            if not jwt or 'role' not in jwt or jwt['role'] != 'employee':
                return jsonify({'message': 'Acesso permitido apenas para funcionários'}), 403
                
            return f(*args, **kwargs)
        return decorated_function

    @staticmethod
    def manager_required(f):
        """Decorator to require manager role"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            jwt = get_jwt()
            
            if not jwt or 'role' not in jwt or jwt['role'] != 'manager':
                return jsonify({'message': 'Acesso permitido apenas para gerentes'}), 403
                
            return f(*args, **kwargs)
        return decorated_function