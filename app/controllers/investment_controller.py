from flask import jsonify, request
from app.services.investment_service import InvestmentService

class InvestmentController:
    @staticmethod
    def get_all_investments():
        investments = InvestmentService.get_all_investments()
        return jsonify([investment.to_dict() for investment in investments]), 200
    
    @staticmethod
    def get_investments_by_employee(employee_id):
        investments = InvestmentService.get_investments_by_employee(employee_id)
        return jsonify([investment.to_dict() for investment in investments]), 200
    
    @staticmethod
    def get_investments_by_credit(credit_id):
        investments = InvestmentService.get_investments_by_credit(credit_id)
        return jsonify([investment.to_dict() for investment in investments]), 200
    
    @staticmethod
    def get_investment_by_id(investment_id):
        investment = InvestmentService.get_investment_by_id(investment_id)
        if not investment:
            return jsonify({"error": "Investment not found"}), 404
        return jsonify(investment.to_dict()), 200
    
    @staticmethod
    def create_investment():
        data = request.get_json()
        
        # Basic validation
        required_fields = ['amount', 'employee_id', 'credit_request_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        investment, error = InvestmentService.create_investment(data)
        if error:
            return jsonify({"error": error}), 400
        
        return jsonify(investment.to_dict()), 201
