from app import db
from datetime import datetime

class Investment(db.Model):
    __tablename__ = 'investments'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    credit_request_id = db.Column(db.Integer, db.ForeignKey('credit_requests.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'employee_id': self.employee_id,
            'credit_request_id': self.credit_request_id,
            'created_at': self.created_at.isoformat()
        }
