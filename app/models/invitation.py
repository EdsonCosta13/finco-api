from app import db
from datetime import datetime
import uuid

class InvitationStatus:
    PENDING = 'pending'
    USED = 'used'
    EXPIRED = 'expired'

class CompanyInvitation(db.Model):
    __tablename__ = 'company_invitations'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)  # Removed unique constraint
    invitation_code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    is_used = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default=InvitationStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='SET NULL'), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'invitation_code': self.invitation_code,
            'is_used': self.is_used,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'company_id': self.company_id,
            'created_by': self.created_by
        }

class EmployeeInvitation(db.Model):
    __tablename__ = 'employee_invitations'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)  # Removed unique constraint
    invitation_code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default=InvitationStatus.PENDING)
    role = db.Column(db.String(20), default='employee')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Relationship
    company = db.relationship('Company', backref='sent_invitations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'invitation_code': self.invitation_code,
            'company_id': self.company_id,
            'is_used': self.is_used,
            'status': self.status,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'created_by': self.created_by,
            'user_id': self.user_id
        }
