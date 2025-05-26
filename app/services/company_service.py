from app import db
from app.models.company import Company
from app.models.user import User
from app.services.invitation_service import InvitationService
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

class CompanyService:
    @staticmethod
    def get_all_companies():
        return Company.query.all()
    
    @staticmethod
    def get_company_by_id(company_id):
        return Company.query.get(company_id)
    
    @staticmethod
    def create_company(data):
        # Validate invitation code
        if 'invitation_code' not in data:
            return None, "Invitation code is required"
        
        valid, invitation_or_error = InvitationService.validate_company_invitation(data['invitation_code'])
        if not valid:
            return None, invitation_or_error
        
        # Verify email matches invitation
        if invitation_or_error.email != data.get('email'):
            return None, "Email does not match the invitation"
        
        try:
            # Create manager user first
            manager_data = data.get('manager', {})
            if not manager_data:
                return None, "Manager information is required"
            
            manager = User(
                name=manager_data.get('name'),
                email=manager_data.get('email'),
                password=generate_password_hash(manager_data.get('password')),
                role='manager'
            )
            db.session.add(manager)
            db.session.flush()  # Get the manager ID without committing
            
            # Create company with manager
            company = Company(
                name=data.get('name'),
                nif=data.get('nif'),
                address=data.get('address'),
                phone=data.get('phone'),
                email=data.get('email'),
                manager_id=manager.id
            )
            
            db.session.add(company)
            
            # Mark invitation as used
            InvitationService.mark_company_invitation_used(invitation_or_error)
            
            db.session.commit()
            return company, None
        except IntegrityError as e:
            db.session.rollback()
            if 'nif' in str(e.orig).lower():
                return None, "nif already exists"
            elif 'email' in str(e.orig).lower():
                return None, "Email already exists"
            return None, str(e)
    
    @staticmethod
    def invite_employee(company_id, employee_email):
        # Verify company exists
        company = Company.query.get(company_id)
        if not company:
            return None, "Company not found"
        
        # Create invitation
        invitation, error = InvitationService.create_employee_invitation(employee_email, company_id)
        if error:
            return None, error
        
        return invitation, None
    
    @staticmethod
    def update_company(company_id, data):
        company = Company.query.get(company_id)
        if not company:
            return None, "Company not found"
        
        try:
            if 'name' in data:
                company.name = data['name']
            if 'address' in data:
                company.address = data['address']
            if 'phone' in data:
                company.phone = data['phone']
            if 'email' in data:
                company.email = data['email']
            
            db.session.commit()
            return company, None
        except IntegrityError as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete_company(company_id):
        company = Company.query.get(company_id)
        if not company:
            return False, "Company not found"
        
        db.session.delete(company)
        db.session.commit()
        return True, None
