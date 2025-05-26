from app import db
from datetime import datetime
import logging

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
    employee = db.relationship('Employee', backref=db.backref('credit_requests', lazy=True, cascade="all, delete-orphan"))
    investments = db.relationship('Investment', backref='credit_request', lazy=True)
    
    def __init__(self, employee_id, amount, term_months, purpose, interest_rate, status=CreditRequestStatus.PENDING):
        self.employee_id = employee_id
        self.amount = amount
        self.term_months = term_months
        self.purpose = purpose
        self.interest_rate = interest_rate
        self.status = status
    
    def to_dict(self):
        try:
            return {
                'id': self.id,
                'amount': self.amount,
                'interest_rate': self.interest_rate,
                'term_months': self.term_months,
                'purpose': self.purpose,
                'status': self.status,
                'employee_id': self.employee_id,
                'employee_name': self.employee.name if self.employee else None,
                'company_name': self.employee.company.name if self.employee and self.employee.company else None,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'funded_amount': sum(investment.amount for investment in self.investments)
            }
        except Exception as e:
            logging.error(f"Erro ao converter solicitação para dicionário: {str(e)}")
            raise
