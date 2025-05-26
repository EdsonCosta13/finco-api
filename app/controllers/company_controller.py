from flask import jsonify, request
from app.services.company_service import CompanyService
from app.services.invitation_service import InvitationService

class CompanyController:
    @staticmethod
    def get_all_companies():
        companies = CompanyService.get_all_companies()
        return jsonify([company.to_dict() for company in companies]), 200
    
    @staticmethod
    def get_company_by_id(company_id):
        company = CompanyService.get_company_by_id(company_id)
        if not company:
            return jsonify({"error": "Company not found"}), 404
        return jsonify(company.to_dict()), 200
    
    @staticmethod
    def create_company():
        data = request.get_json()
        
        # Basic validation
        required_fields = ['name', 'nif', 'email', 'invitation_code']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate manager data
        if 'manager' not in data:
            return jsonify({"error": "Manager information is required"}), 400
        
        manager_data = data['manager']
        required_manager_fields = ['name', 'email', 'password']
        for field in required_manager_fields:
            if field not in manager_data:
                return jsonify({"error": f"Missing required manager field: {field}"}), 400
        
        # Validate the invitation code before creating the company
        invitation_code = data['invitation_code']
        valid, result = InvitationService.validate_company_invitation(invitation_code)
        
        if not valid:
            return jsonify({"message": "Código de convite inválido ou expirado"}), 400
            
        # Include the validated invitation in the data
        data['invitation'] = result
        
        company, error = CompanyService.create_company(data)
        if error:
            return jsonify({"error": error}), 400
        
        # Mark invitation as used only after successful company creation
        InvitationService.mark_company_invitation_used(result)
        
        return jsonify(company.to_dict()), 201
    
    @staticmethod
    def update_company(company_id):
        data = request.get_json()
        company, error = CompanyService.update_company(company_id, data)
        
        if error:
            return jsonify({"error": error}), 400
        
        return jsonify(company.to_dict()), 200
    
    @staticmethod
    def delete_company(company_id):
        success, error = CompanyService.delete_company(company_id)
        
        if not success:
            return jsonify({"error": error}), 404
        
        return jsonify({"message": "Company deleted successfully"}), 200
