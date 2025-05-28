from app import db
from datetime import datetime
import logging

class Investment(db.Model):
    __tablename__ = 'investments'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    credit_request_id = db.Column(db.Integer, db.ForeignKey('credit_requests.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        try:
            # Calcula o total de pagamentos recebidos
            total_paid = sum(
                payment.amount 
                for payment in self.payments 
                if payment.status == 'paid'
            )
            
            # Calcula o total de pagamentos pendentes
            total_pending = sum(
                payment.amount 
                for payment in self.payments 
                if payment.status == 'pending'
            )
            
            # Calcula o total de juros a receber
            total_interest = sum(
                payment.amount 
                for payment in self.payments 
                if payment.type == 'interest' and payment.status == 'pending'
            )
            
            # Calcula o total de dividendos a receber
            total_dividend = sum(
                payment.amount 
                for payment in self.payments 
                if payment.type == 'dividend' and payment.status == 'pending'
            )
            
            return {
                'id': self.id,
                'amount': self.amount,
                'employee_id': self.employee_id,
                'credit_request_id': self.credit_request_id,
                'created_at': self.created_at.isoformat(),
                'credit_request': {
                    'id': self.credit_request.id,
                    'amount': self.credit_request.amount,
                    'interest_rate': self.credit_request.interest_rate,
                    'term_months': self.credit_request.term_months,
                    'purpose': self.credit_request.purpose,
                    'status': self.credit_request.status,
                    'employee_name': self.credit_request.employee.name,
                    'company_name': self.credit_request.employee.company.name,
                    'created_at': self.credit_request.created_at.isoformat(),
                    'funded_amount': sum(inv.amount for inv in self.credit_request.investments),
                    'investment_percentage': (sum(inv.amount for inv in self.credit_request.investments) / self.credit_request.amount) * 100
                },
                'payments_summary': {
                    'total_paid': total_paid,
                    'total_pending': total_pending,
                    'total_interest': total_interest,
                    'total_dividend': total_dividend,
                    'next_payment': min(
                        (p for p in self.payments if p.status == 'pending'),
                        key=lambda p: p.due_date
                    ).to_dict() if any(p.status == 'pending' for p in self.payments) else None
                },
                'payments': [payment.to_dict() for payment in self.payments]
            }
        except Exception as e:
            logging.error(f"Erro ao converter investimento para dicionário: {str(e)}")
            raise
