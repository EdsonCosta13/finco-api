from app import db
from app.models.company import Company
from app.services.invitation_service import InvitationService
from sqlalchemy.exc import IntegrityError

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
            company = Company(
                name=data.get('name'),
                cnpj=data.get('cnpj'),
                address=data.get('address'),
                phone=data.get('phone'),
                email=data.get('email')
            )
            
            db.session.add(company)
            
            # Mark invitation as used
            InvitationService.mark_company_invitation_used(invitation_or_error)
            
            db.session.commit()
            return company, None
        except IntegrityError as e:
            db.session.rollback()
            if 'cnpj' in str(e.orig).lower():
                return None, "CNPJ already exists"
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
