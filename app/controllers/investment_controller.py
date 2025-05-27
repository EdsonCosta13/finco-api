from flask import jsonify, request
from app.services.investment_service import InvestmentService
from app.models.credit_request import CreditRequestStatus
from flask_jwt_extended import get_jwt
import logging

class InvestmentController:
    @staticmethod
    def get_all_investments():
        try:
            investments = InvestmentService.get_all_investments()
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Investimentos encontrados',
                'data': [investment.to_dict() for investment in investments],
                'total': len(investments)
            }), 200
        except Exception as e:
            logging.error(f"Erro ao buscar investimentos: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao buscar investimentos: {str(e)}'
            }), 500
    
    @staticmethod
    def get_investments_by_employee(employee_id):
        try:
            investments = InvestmentService.get_investments_by_employee(employee_id)
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Investimentos do funcionário encontrados',
                'data': [investment.to_dict() for investment in investments],
                'total': len(investments)
            }), 200
        except Exception as e:
            logging.error(f"Erro ao buscar investimentos do funcionário: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao buscar investimentos: {str(e)}'
            }), 500
    
    @staticmethod
    def get_investments_by_credit(credit_id):
        try:
            investments = InvestmentService.get_investments_by_credit(credit_id)
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Investimentos da solicitação encontrados',
                'data': [investment.to_dict() for investment in investments],
                'total': len(investments)
            }), 200
        except Exception as e:
            logging.error(f"Erro ao buscar investimentos da solicitação: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao buscar investimentos: {str(e)}'
            }), 500
    
    @staticmethod
    def get_investment_by_id(investment_id):
        try:
            investment = InvestmentService.get_investment_by_id(investment_id)
            if not investment:
                return jsonify({
                    'status': 'error',
                    'statusCode': 404,
                    'message': 'Investimento não encontrado'
                }), 404
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Investimento encontrado',
                'data': investment.to_dict()
            }), 200
        except Exception as e:
            logging.error(f"Erro ao buscar investimento: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao buscar investimento: {str(e)}'
            }), 500
    
    @staticmethod
    def list_investment_opportunities():
        try:
            opportunities = InvestmentService.get_available_opportunities()
            
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Oportunidades de investimento encontradas',
                'data': opportunities,
                'total': len(opportunities)
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao buscar oportunidades: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao buscar oportunidades: {str(e)}'
            }), 500
    
    @staticmethod
    def create_investment():
        try:
            data = request.get_json()
            jwt = get_jwt()
            
            if not data:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': 'Dados não fornecidos'
                }), 400
            
            # Validate required fields
            required_fields = ['credit_request_id', 'amount']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'status': 'error',
                        'statusCode': 400,
                        'message': f'O campo {field} é obrigatório'
                    }), 400
            
            # Get employee_id from JWT claims
            employee_id = jwt.get('employee_id')
            if not employee_id:
                return jsonify({
                    'status': 'error',
                    'statusCode': 401,
                    'message': 'ID do funcionário não encontrado no token'
                }), 401
            
            # Create investment
            result = InvestmentService.create_investment(
                employee_id=employee_id,
                credit_request_id=data['credit_request_id'],
                amount=float(data['amount'])
            )
            
            if isinstance(result, tuple):
                return jsonify({
                    'status': 'error',
                    'statusCode': result[1],
                    'message': result[0]
                }), result[1]
            
            return jsonify({
                'status': 'success',
                'statusCode': 201,
                'message': 'Investimento realizado com sucesso',
                'data': result
            }), 201
            
        except ValueError as e:
            return jsonify({
                'status': 'error',
                'statusCode': 400,
                'message': str(e)
            }), 400
        except Exception as e:
            logging.error(f"Erro ao realizar investimento: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao realizar investimento: {str(e)}'
            }), 500
