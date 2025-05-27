from app import db
from datetime import datetime
import logging

class TransactionType:
    DEPOSIT = 'deposit'  # Carregamento de saldo
    INVESTMENT = 'investment'  # Investimento em crédito
    DIVIDEND = 'dividend'  # Recebimento de dividendos
    INTEREST = 'interest'  # Recebimento de juros
    WITHDRAWAL = 'withdrawal'  # Saque de saldo

class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    investment_id = db.Column(db.Integer, db.ForeignKey('investments.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    investment = db.relationship('Investment', backref=db.backref('wallet_transactions', lazy=True))
    
    def __init__(self, wallet_id, type, amount, description=None, investment_id=None):
        self.wallet_id = wallet_id
        self.type = type
        self.amount = amount
        self.description = description
        self.investment_id = investment_id
    
    def to_dict(self):
        try:
            return {
                'id': self.id,
                'wallet_id': self.wallet_id,
                'type': self.type,
                'amount': self.amount,
                'description': self.description,
                'investment_id': self.investment_id,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'employee_name': self.wallet.employee.name if self.wallet and self.wallet.employee else None
            }
        except Exception as e:
            logging.error(f"Erro ao converter transação para dicionário: {str(e)}")
            raise 