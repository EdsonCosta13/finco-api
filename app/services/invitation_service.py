from app import db
from app.models.invitation import CompanyInvitation, EmployeeInvitation, InvitationStatus
from app.utils.email import send_invitation_email
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import uuid

class InvitationService:
    # Default expiration period for invitations (in days)
    INVITATION_EXPIRY_DAYS = 7
    
    @staticmethod
    def create_company_invitation(email, created_by=None):
        """Create an invitation for a company to register"""
        try:
            # Check if an active invitation already exists
            existing_invitation = CompanyInvitation.query.filter_by(
                email=email, 
                is_used=False,
                status=InvitationStatus.PENDING
            ).first()
            
            if existing_invitation and existing_invitation.expires_at > datetime.utcnow():
                # Send email with the existing invitation
                send_invitation_email(existing_invitation, 'company')
                return existing_invitation, None
            
            # Create new invitation
            invitation = CompanyInvitation(
                email=email,
                invitation_code=str(uuid.uuid4()),
                expires_at=datetime.utcnow() + timedelta(days=InvitationService.INVITATION_EXPIRY_DAYS),
                created_by=created_by,
                status=InvitationStatus.PENDING
            )
            
            db.session.add(invitation)
            db.session.commit()
            
            # Send email with the new invitation
            send_invitation_email(invitation, 'company')
            
            return invitation, None
            
        except IntegrityError as e:
            db.session.rollback()
            return None, str(e)
        except Exception as e:
            db.session.rollback()
            return None, f"Error creating invitation: {str(e)}"
    
    @staticmethod
    def validate_company_invitation(invitation_code):
        """Validate a company invitation code"""
        if not invitation_code or not isinstance(invitation_code, str):
            return False, "Invalid invitation code format"
            
        # Normalize the invitation code (trim whitespace and ensure lowercase)
        invitation_code = invitation_code.strip()
        
        invitation = CompanyInvitation.query.filter_by(invitation_code=invitation_code).first()
        
        if not invitation:
            return False, "Invalid invitation code"
        
        if invitation.is_used or invitation.status == InvitationStatus.USED:
            return False, "Invitation has already been used"
        
        if invitation.expires_at < datetime.utcnow():
            invitation.status = InvitationStatus.EXPIRED
            db.session.commit()
            return False, "Invitation has expired"
        
        return True, invitation
    
    @staticmethod
    def mark_company_invitation_used(invitation):
        """Mark a company invitation as used"""
        invitation.is_used = True
        invitation.status = InvitationStatus.USED
        db.session.commit()
    
    @staticmethod
    def create_employee_invitation(email, company_id, created_by=None, role='employee'):
        """Create an invitation for an employee to register"""
        try:
            # Check if an active invitation already exists
            existing_invitation = EmployeeInvitation.query.filter_by(
                email=email, 
                is_used=False,
                company_id=company_id,
                status=InvitationStatus.PENDING
            ).first()
            
            if existing_invitation and existing_invitation.expires_at > datetime.utcnow():
                # Send email with the existing invitation
                send_invitation_email(existing_invitation, 'employee')
                return existing_invitation, None
            
            # Create new invitation
            invitation = EmployeeInvitation(
                email=email,
                company_id=company_id,
                invitation_code=str(uuid.uuid4()),
                expires_at=datetime.utcnow() + timedelta(days=InvitationService.INVITATION_EXPIRY_DAYS),
                created_by=created_by,
                role=role,
                status=InvitationStatus.PENDING
            )
            
            db.session.add(invitation)
            db.session.commit()
            
            # Send email with the new invitation
            send_invitation_email(invitation, 'employee')
            
            return invitation, None
            
        except IntegrityError as e:
            db.session.rollback()
            return None, str(e)
        except Exception as e:
            db.session.rollback()
            return None, f"Error creating invitation: {str(e)}"
    
    @staticmethod
    def validate_employee_invitation(invitation_code):
        """Validate an employee invitation code"""
        invitation = EmployeeInvitation.query.filter_by(invitation_code=invitation_code).first()
        
        if not invitation:
            return False, "Invalid invitation code"
        
        if invitation.is_used or invitation.status == InvitationStatus.USED:
            return False, "Invitation has already been used"
        
        if invitation.expires_at < datetime.utcnow():
            invitation.status = InvitationStatus.EXPIRED
            db.session.commit()
            return False, "Invitation has expired"
        
        return True, invitation
    
    @staticmethod
    def mark_employee_invitation_used(invitation):
        """Mark an employee invitation as used"""
        invitation.is_used = True
        invitation.status = InvitationStatus.USED
        db.session.commit()
