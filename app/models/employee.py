from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    position = db.Column(db.String(50))
    salary = db.Column(db.Float, nullable=False)
    phone = db.Column(db.String(20))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    credit_requests = db.relationship('CreditRequest', backref='employee', lazy=True, cascade="all, delete-orphan")
    investments = db.relationship('Investment', backref='employee', lazy=True, cascade="all, delete-orphan")
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'cpf': self.cpf,
            'position': self.position,
            'salary': self.salary,
            'phone': self.phone,
            'company_id': self.company_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
