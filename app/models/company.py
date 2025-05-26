from app import db
from datetime import datetime

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    nif = db.Column(db.String(14), unique=True, nullable=False)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employees = db.relationship('Employee', backref=db.backref('company', lazy=True), lazy=True, cascade="all, delete-orphan")
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    manager = db.relationship('User', foreign_keys=[manager_id], backref='managed_companies')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'nif': self.nif,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'manager_id': self.manager_id
        }
