from app import db
from datetime import datetime
import logging

class PaymentType:
    DIVIDEND = 'dividend'  # Pagamento de dividendos
    INTEREST = 'interest'  # Pagamento de juros

class PaymentStatus:
    PENDING = 'pending'  # Pagamento pendente
    PAID = 'paid'  # Pagamento realizado
    FAILED = 'failed'  # Falha no pagamento

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    investment_id = db.Column(db.Integer, db.ForeignKey('investments.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # dividend ou interest
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default=PaymentStatus.PENDING)
    due_date = db.Column(db.DateTime, nullable=False)
    paid_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    investment = db.relationship('Investment', backref=db.backref('payments', lazy=True))
    
    def __init__(self, investment_id, type, amount, due_date):
        self.investment_id = investment_id
        self.type = type
        self.amount = amount
        self.due_date = due_date
    
    def to_dict(self):
        try:
            return {
                'id': self.id,
                'investment_id': self.investment_id,
                'type': self.type,
                'amount': self.amount,
                'status': self.status,
                'due_date': self.due_date.isoformat() if self.due_date else None,
                'paid_at': self.paid_at.isoformat() if self.paid_at else None,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'employee_name': self.investment.employee.name if self.investment and self.investment.employee else None,
                'credit_request_id': self.investment.credit_request_id if self.investment else None
            }
        except Exception as e:
            logging.error(f"Erro ao converter pagamento para dicionário: {str(e)}")
            raise
    
    def mark_as_paid(self):
        """Marca o pagamento como realizado"""
        self.status = PaymentStatus.PAID
        self.paid_at = datetime.utcnow()
    
    def mark_as_failed(self):
        """Marca o pagamento como falho"""
        self.status = PaymentStatus.FAILED 