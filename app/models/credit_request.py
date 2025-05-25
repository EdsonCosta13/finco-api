from app import db
from datetime import datetime

class CreditRequestStatus:
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'
    FUNDED = 'funded'
    COMPLETED = 'completed'

class CreditRequest(db.Model):
    __tablename__ = 'credit_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    term_months = db.Column(db.Integer, nullable=False)
    purpose = db.Column(db.String(200))
    status = db.Column(db.String(20), default=CreditRequestStatus.PENDING)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    investments = db.relationship('Investment', backref='credit_request', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'interest_rate': self.interest_rate,
            'term_months': self.term_months,
            'purpose': self.purpose,
            'status': self.status,
            'employee_id': self.employee_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'funded_amount': sum(investment.amount for investment in self.investments)
        }
