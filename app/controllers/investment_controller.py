from flask import jsonify, request
from app.services.investment_service import InvestmentService
from app.models.credit_request import CreditRequestStatus
from flask_jwt_extended import get_jwt
import logging

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
    def list_investment_opportunities():
        try:
            # Get all pending credit requests that are available for investment
            opportunities = InvestmentService.get_available_opportunities()
            
            return jsonify({
                'message': 'Oportunidades de investimento encontradas',
                'opportunities': opportunities
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao buscar oportunidades: {str(e)}")
            return jsonify({'message': f'Erro ao buscar oportunidades: {str(e)}'}), 500
    
    @staticmethod
    def create_investment():
        try:
            data = request.get_json()
            jwt = get_jwt()
            
            if not data:
                return jsonify({'message': 'Dados não fornecidos'}), 400
            
            # Validate required fields
            required_fields = ['credit_request_id', 'amount']
            for field in required_fields:
                if field not in data:
                    return jsonify({'message': f'O campo {field} é obrigatório'}), 400
            
            # Get employee_id from JWT claims
            employee_id = jwt.get('employee_id')
            if not employee_id:
                return jsonify({'message': 'ID do funcionário não encontrado no token'}), 401
            
            # Create investment
            result = InvestmentService.create_investment(
                employee_id=employee_id,
                credit_request_id=data['credit_request_id'],
                amount=float(data['amount'])
            )
            
            if isinstance(result, tuple):
                return jsonify({'message': result[0]}), result[1]
            
            return jsonify({
                'message': 'Investimento realizado com sucesso',
                'investment': result
            }), 201
            
        except ValueError as e:
            return jsonify({'message': str(e)}), 400
        except Exception as e:
            logging.error(f"Erro ao realizar investimento: {str(e)}")
            return jsonify({'message': f'Erro ao realizar investimento: {str(e)}'}), 500
