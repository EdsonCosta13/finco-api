from app import db
from datetime import datetime
import uuid

class CompanyInvitation(db.Model):
    __tablename__ = 'company_invitations'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    invitation_code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'invitation_code': self.invitation_code,
            'is_used': self.is_used,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat()
        }

class EmployeeInvitation(db.Model):
    __tablename__ = 'employee_invitations'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    invitation_code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    # Relationship
    company = db.relationship('Company', backref='sent_invitations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'invitation_code': self.invitation_code,
            'company_id': self.company_id,
            'is_used': self.is_used,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat()
        }
