from app import db
from app.models.credit_request import CreditRequest, CreditRequestStatus
from app.models.employee import Employee
from sqlalchemy.exc import IntegrityError

class CreditService:
    @staticmethod
    def get_all_credit_requests():
        return CreditRequest.query.all()
    
    @staticmethod
    def get_credit_requests_by_employee(employee_id):
        return CreditRequest.query.filter_by(employee_id=employee_id).all()
    
    @staticmethod
    def get_credit_request_by_id(credit_id):
        return CreditRequest.query.get(credit_id)
    
    @staticmethod
    def create_credit_request(data):
        # Check if employee exists
        employee = Employee.query.get(data.get('employee_id'))
        if not employee:
            return None, "Employee not found"
        
        # Check if employee has pending credit requests
        pending_requests = CreditRequest.query.filter_by(
            employee_id=data.get('employee_id'),
            status=CreditRequestStatus.PENDING
        ).first()
        
        if pending_requests:
            return None, "Employee already has a pending credit request"
        
        try:
            credit_request = CreditRequest(
                amount=data.get('amount'),
                interest_rate=data.get('interest_rate'),
                term_months=data.get('term_months'),
                purpose=data.get('purpose'),
                status=CreditRequestStatus.PENDING,
                employee_id=data.get('employee_id')
            )
            
            db.session.add(credit_request)
            db.session.commit()
            return credit_request, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def update_credit_request_status(credit_id, status):
        credit_request = CreditRequest.query.get(credit_id)
        if not credit_request:
            return None, "Credit request not found"
        
        # Validate status transition
        if credit_request.status == CreditRequestStatus.COMPLETED:
            return None, "Cannot change status of completed credit request"
        
        if credit_request.status == CreditRequestStatus.REJECTED and status != CreditRequestStatus.CANCELLED:
            return None, "Rejected credit requests can only be cancelled"
        
        # Apply status update
        credit_request.status = status
        db.session.commit()
        return credit_request, None
    
    @staticmethod
    def get_funded_amount(credit_id):
        credit_request = CreditRequest.query.get(credit_id)
        if not credit_request:
            return 0
        
        return sum(investment.amount for investment in credit_request.investments)
    
    @staticmethod
    def check_fully_funded(credit_request):
        funded_amount = CreditService.get_funded_amount(credit_request.id)
        if funded_amount >= credit_request.amount:
            credit_request.status = CreditRequestStatus.FUNDED
            db.session.commit()
            return True
        return False
