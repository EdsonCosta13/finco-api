from app import db
from datetime import datetime
import logging

class Wallet(db.Model):
    __tablename__ = 'wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = db.relationship('Employee', backref=db.backref('wallet', uselist=False))
    transactions = db.relationship('WalletTransaction', backref='wallet', lazy=True)
    
    def __init__(self, employee_id, balance=0.0):
        self.employee_id = employee_id
        self.balance = balance
    
    def to_dict(self):
        try:
            return {
                'id': self.id,
                'employee_id': self.employee_id,
                'balance': self.balance,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'employee_name': self.employee.name if self.employee else None
            }
        except Exception as e:
            logging.error(f"Erro ao converter carteira para dicionário: {str(e)}")
            raise
    
    def add_balance(self, amount):
        """Adiciona saldo à carteira"""
        if amount <= 0:
            raise ValueError("O valor deve ser maior que zero")
        self.balance += amount
        return self.balance
    
    def subtract_balance(self, amount):
        """Subtrai saldo da carteira"""
        if amount <= 0:
            raise ValueError("O valor deve ser maior que zero")
        if amount > self.balance:
            raise ValueError("Saldo insuficiente")
        self.balance -= amount
        return self.balance 