from flask import jsonify, request
from app.services.invitation_service import InvitationService
from app.services.company_service import CompanyService

class InvitationController:
    @staticmethod
    def create_company_invitation():
        data = request.get_json()
        
        # Validate required fields
        if 'email' not in data:
            return jsonify({"error": "Email is required"}), 400
        
        # Create company invitation
        invitation, error = InvitationService.create_company_invitation(data['email'])
        if error:
            return jsonify({"error": error}), 400
        
        # Email is sent within the service
        return jsonify({
            "message": "Invitation created and email sent successfully",
            "invitation": invitation.to_dict()
        }), 201
    
    @staticmethod
    def create_employee_invitation():
        data = request.get_json()
        
        # Validate required fields
        if 'email' not in data:
            return jsonify({"error": "Email is required"}), 400
        if 'company_id' not in data:
            return jsonify({"error": "Company ID is required"}), 400
        
        # Create employee invitation
        invitation, error = CompanyService.invite_employee(data['company_id'], data['email'])
        if error:
            return jsonify({"error": error}), 400
        
        # Email is sent within the service
        return jsonify({
            "message": "Invitation created and email sent successfully",
            "invitation": invitation.to_dict()
        }), 201
    
    @staticmethod
    def validate_invitation():
        data = request.get_json()
        
        # Validate required fields
        if 'invitation_code' not in data:
            return jsonify({"error": "Invitation code is required"}), 400
        if 'type' not in data:
            return jsonify({"error": "Invitation type is required (company or employee)"}), 400
        
        # Validate invitation based on type
        invitation_type = data['type'].lower()
        if invitation_type == 'company':
            valid, result = InvitationService.validate_company_invitation(data['invitation_code'])
        elif invitation_type == 'employee':
            valid, result = InvitationService.validate_employee_invitation(data['invitation_code'])
        else:
            return jsonify({"error": "Invalid invitation type (must be 'company' or 'employee')"}), 400
        
        if not valid:
            return jsonify({"error": result}), 400
        
        # Return the invitation details
        return jsonify({
            "valid": True,
            "invitation": result.to_dict()
        }), 200
