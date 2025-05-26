from app import db
from app.models.employee import Employee
from app.models.company import Company
from app.models.invitation import EmployeeInvitation, InvitationStatus
from app.services.invitation_service import InvitationService
from sqlalchemy.exc import IntegrityError

class EmployeeService:
    @staticmethod
    def get_all_employees():
        return Employee.query.all()
    
    @staticmethod
    def get_employees_by_company(company_id):
        return Employee.query.filter_by(company_id=company_id).all()
    
    @staticmethod
    def get_employee_by_id(employee_id):
        return Employee.query.get(employee_id)
    
    @staticmethod
    def create_employee(data):
        # Validate invitation code
        if 'invitation_code' not in data:
            return None, "Invitation code is required"
        
        valid, invitation_or_error = InvitationService.validate_employee_invitation(data['invitation_code'])
        if not valid:
            return None, invitation_or_error
        
        # Verify email matches invitation
        if invitation_or_error.email != data.get('email'):
            return None, "Email does not match the invitation"
        
        # Set company_id from the invitation
        company_id = invitation_or_error.company_id
        
        try:
            employee = Employee(
                name=data.get('name'),
                email=data.get('email'),
                cpf=data.get('cpf'),
                position=data.get('position'),
                salary=data.get('salary'),
                phone=data.get('phone'),
                company_id=company_id
            )
            
            if 'password' in data:
                employee.password = data['password']
            
            db.session.add(employee)
            
            # Mark invitation as used
            invitation_or_error.is_used = True
            invitation_or_error.status = InvitationStatus.USED
            
            db.session.commit()
            return employee, None
        except IntegrityError as e:
            db.session.rollback()
            if 'cpf' in str(e.orig).lower():
                return None, "CPF already exists"
            elif 'email' in str(e.orig).lower():
                return None, "Email already exists"
            return None, str(e)
    
    @staticmethod
    def update_employee(employee_id, data):
        employee = Employee.query.get(employee_id)
        if not employee:
            return None, "Employee not found"
        
        try:
            if 'name' in data:
                employee.name = data['name']
            if 'email' in data:
                employee.email = data['email']
            if 'position' in data:
                employee.position = data['position']
            if 'salary' in data:
                employee.salary = data['salary']
            if 'phone' in data:
                employee.phone = data['phone']
            if 'password' in data:
                employee.password = data['password']
            
            db.session.commit()
            return employee, None
        except IntegrityError as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete_employee(employee_id):
        employee = Employee.query.get(employee_id)
        if not employee:
            return False, "Employee not found"
        
        db.session.delete(employee)
        db.session.commit()
        return True, None

    @staticmethod
    def register_employee(data):
        """
        Register a new employee from an invitation code
        """
        # Validate invitation code
        if 'invitation_code' not in data:
            return None, "Invitation code is required"
        
        valid, invitation_or_error = InvitationService.validate_employee_invitation(data['invitation_code'])
        if not valid:
            return None, invitation_or_error
        
        # Verify email matches invitation
        if invitation_or_error.email.lower() != data.get('email', '').lower():
            return None, "Email does not match the invitation"
        
        # Set company_id from the invitation
        company_id = invitation_or_error.company_id
        
        try:
            employee = Employee(
                name=data.get('name'),
                email=data.get('email'),
                cpf=data.get('cpf'),
                position=data.get('position'),
                salary=data.get('salary'),
                phone=data.get('phone'),
                company_id=company_id
            )
            
            if 'password' in data:
                employee.password = data['password']
            
            db.session.add(employee)
            
            # Mark invitation as used
            invitation_or_error.is_used = True
            invitation_or_error.status = InvitationStatus.USED
            
            db.session.commit()
            return employee, None
        except IntegrityError as e:
            db.session.rollback()
            if 'cpf' in str(e.orig).lower():
                return None, "CPF already exists"
            elif 'email' in str(e.orig).lower():
                return None, "Email already exists"
            return None, str(e)
