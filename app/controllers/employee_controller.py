from flask import jsonify, request
from app.services.employee_service import EmployeeService
from app.services.invitation_service import InvitationService
from app.models.invitation import InvitationStatus

class EmployeeController:
    @staticmethod
    def get_all_employees():
        employees = EmployeeService.get_all_employees()
        return jsonify([employee.to_dict() for employee in employees]), 200
    
    @staticmethod
    def get_employees_by_company(company_id):
        employees = EmployeeService.get_employees_by_company(company_id)
        return jsonify([employee.to_dict() for employee in employees]), 200
    
    @staticmethod
    def get_employee_by_id(employee_id):
        employee = EmployeeService.get_employee_by_id(employee_id)
        if not employee:
            return jsonify({"error": "Employee not found"}), 404
        return jsonify(employee.to_dict()), 200
    
    @staticmethod
    def create_employee():
        data = request.get_json()
        
        # Basic validation
        required_fields = ['name', 'email', 'cpf', 'salary', 'company_id', 'password', 'invitation_code']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate invitation code
        valid, invitation_or_error = InvitationService.validate_employee_invitation(data['invitation_code'])
        if not valid:
            return jsonify({"error": invitation_or_error}), 400
        
        # Verify email matches invitation
        if invitation_or_error.email.lower().strip() != data['email'].lower().strip():
            return jsonify({"error": "O email não corresponde ao convite"}), 400
        
        # Verify company matches invitation
        if invitation_or_error.company_id != data['company_id']:
            return jsonify({"error": "A empresa não corresponde ao convite"}), 400
        
        employee, error = EmployeeService.create_employee(data)
        if error:
            return jsonify({"error": error}), 400
        
        # Mark invitation as used
        InvitationService.mark_employee_invitation_used(invitation_or_error)
        
        return jsonify(employee.to_dict()), 201
    
    @staticmethod
    def invite_employee():
        data = request.get_json()
        
        # Basic validation
        required_fields = ['email', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Optional role field
        role = data.get('role', 'employee')
        
        # Create invitation
        invitation, error = InvitationService.create_employee_invitation(
            email=data['email'],
            company_id=data['company_id'],
            role=role
        )
        
        if error:
            return jsonify({"error": error}), 400
        
        return jsonify({
            "message": "Convite enviado com sucesso",
            "invitation": {
                "email": invitation.email,
                "company_id": invitation.company_id,
                "role": invitation.role,
                "expires_at": invitation.expires_at.isoformat()
            }
        }), 201
    
    @staticmethod
    def update_employee(employee_id):
        data = request.get_json()
        employee, error = EmployeeService.update_employee(employee_id, data)
        
        if error:
            return jsonify({"error": error}), 400
        
        return jsonify(employee.to_dict()), 200
    
    @staticmethod
    def delete_employee(employee_id):
        success, error = EmployeeService.delete_employee(employee_id)
        
        if not success:
            return jsonify({"error": error}), 404
        
        return jsonify({"message": "Employee deleted successfully"}), 200
    
    @staticmethod
    def register_employee():
        data = request.get_json()
        
        # Basic validation
        required_fields = ['name', 'email', 'cpf', 'position', 'salary', 'phone', 'password', 'invitation_code']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate invitation code
        valid, invitation_or_error = InvitationService.validate_employee_invitation(data['invitation_code'])
        if not valid:
            return jsonify({"error": invitation_or_error}), 400
        
        # Verify email matches invitation
        if invitation_or_error.email.lower().strip() != data['email'].lower().strip():
            return jsonify({"error": "O email não corresponde ao convite"}), 400
        
        employee, error = EmployeeService.register_employee(data)
        if error:
            return jsonify({"error": error}), 400
        
        # Mark invitation as used
        invitation_or_error.status = InvitationStatus.USED
        
        return jsonify({
            "message": "Funcionário registrado com sucesso",
            "employee": employee.to_dict()
        }), 201
