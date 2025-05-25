from flask import jsonify, request
from app.services.credit_service import CreditService
from app.models.credit_request import CreditRequestStatus

class CreditController:
    @staticmethod
    def get_all_credit_requests():
        credits = CreditService.get_all_credit_requests()
        return jsonify([credit.to_dict() for credit in credits]), 200
    
    @staticmethod
    def get_credit_requests_by_employee(employee_id):
        credits = CreditService.get_credit_requests_by_employee(employee_id)
        return jsonify([credit.to_dict() for credit in credits]), 200
    
    @staticmethod
    def get_credit_request_by_id(credit_id):
        credit = CreditService.get_credit_request_by_id(credit_id)
        if not credit:
            return jsonify({"error": "Credit request not found"}), 404
        return jsonify(credit.to_dict()), 200
    
    @staticmethod
    def create_credit_request():
        data = request.get_json()
        
        # Basic validation
        required_fields = ['amount', 'interest_rate', 'term_months', 'employee_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        credit_request, error = CreditService.create_credit_request(data)
        if error:
            return jsonify({"error": error}), 400
        
        return jsonify(credit_request.to_dict()), 201
    
    @staticmethod
    def update_credit_status(credit_id):
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({"error": "Status field is required"}), 400
        
        # Validate status value
        status = data['status']
        valid_statuses = [s for s in dir(CreditRequestStatus) if not s.startswith('_')]
        
        if status not in valid_statuses:
            return jsonify({"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400
        
        credit_request, error = CreditService.update_credit_request_status(credit_id, status)
        
        if error:
            return jsonify({"error": error}), 400
        
        return jsonify(credit_request.to_dict()), 200
