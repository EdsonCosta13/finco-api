from app import db
from app.models.investment import Investment
from app.models.employee import Employee
from app.models.credit_request import CreditRequest, CreditRequestStatus
from app.services.credit_service import CreditService

class InvestmentService:
    # Minimum investment amount
    MIN_INVESTMENT_AMOUNT = 100.0
    
    @staticmethod
    def get_all_investments():
        return Investment.query.all()
    
    @staticmethod
    def get_investments_by_employee(employee_id):
        return Investment.query.filter_by(employee_id=employee_id).all()
    
    @staticmethod
    def get_investments_by_credit(credit_id):
        return Investment.query.filter_by(credit_request_id=credit_id).all()
    
    @staticmethod
    def get_investment_by_id(investment_id):
        return Investment.query.get(investment_id)
    
    @staticmethod
    def create_investment(data):
        # Validate employee
        employee = Employee.query.get(data.get('employee_id'))
        if not employee:
            return None, "Employee not found"
        
        # Validate credit request
        credit_request = CreditRequest.query.get(data.get('credit_request_id'))
        if not credit_request:
            return None, "Credit request not found"
        
        # Validate credit request status
        if credit_request.status != CreditRequestStatus.APPROVED:
            return None, "Cannot invest in a credit request that is not approved"
        
        # Validate investment amount
        amount = data.get('amount')
        if amount < InvestmentService.MIN_INVESTMENT_AMOUNT:
            return None, f"Investment amount must be at least {InvestmentService.MIN_INVESTMENT_AMOUNT}"
        
        # Check if employee is trying to invest in their own credit request
        if employee.id == credit_request.employee_id:
            return None, "Cannot invest in your own credit request"
        
        # Check if investment would exceed required amount
        current_funding = CreditService.get_funded_amount(credit_request.id)
        remaining = credit_request.amount - current_funding
        
        if amount > remaining:
            return None, f"Investment would exceed required amount. Maximum: {remaining}"
        
        try:
            investment = Investment(
                amount=amount,
                employee_id=employee.id,
                credit_request_id=credit_request.id
            )
            
            db.session.add(investment)
            db.session.commit()
            
            # Check if credit is now fully funded
            CreditService.check_fully_funded(credit_request)
            
            return investment, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
