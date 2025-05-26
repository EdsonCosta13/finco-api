from flask import jsonify, request
from app.services.credit_service import CreditService
from app.models.credit_request import CreditRequestStatus
from flask_jwt_extended import get_jwt
import logging

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
    def create_employee_credit_request():
        try:
            data = request.get_json()
            jwt = get_jwt()
            
            if not data:
                return jsonify({'message': 'Dados não fornecidos'}), 400
                
            # Get employee_id from JWT claims
            employee_id = jwt.get('employee_id')
            if not employee_id:
                return jsonify({'message': 'ID do funcionário não encontrado no token'}), 401
            
            # Validate required fields
            required_fields = ['amount', 'term_months', 'purpose']
            for field in required_fields:
                if field not in data:
                    return jsonify({'message': f'O campo {field} é obrigatório'}), 400
            
            # Create credit request
            result = CreditService.create_employee_credit_request(
                employee_id=employee_id,
                amount=float(data['amount']),
                term_months=int(data['term_months']),
                purpose=data['purpose']
            )
            
            if isinstance(result, tuple):
                return jsonify({'message': result[0]}), result[1]
                
            return jsonify({
                'message': 'Solicitação de crédito criada com sucesso',
                'credit_request': result
            }), 201
            
        except ValueError as e:
            return jsonify({'message': str(e)}), 400
        except Exception as e:
            return jsonify({'message': f'Erro ao criar solicitação de crédito: {str(e)}'}), 500
    
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
    def update_credit_status(credit_id, status):
        """Atualiza o status de uma solicitação de crédito"""
        try:
            result = CreditService.update_credit_request_status(credit_id, status)
            
            if isinstance(result, tuple):
                return jsonify({'message': result[1]}), 400
                
            return jsonify({
                'message': f'Solicitação de crédito {status} com sucesso',
                'credit_request': result.to_dict()
            }), 200
            
        except Exception as e:
            return jsonify({'message': f'Erro ao atualizar status: {str(e)}'}), 500

    @staticmethod
    def get_employee_credit_requests():
        """Lista as solicitações de crédito do funcionário"""
        try:
            jwt = get_jwt()
            employee_id = jwt.get('employee_id')
            
            if not employee_id:
                return jsonify({'message': 'ID do funcionário não encontrado no token'}), 401
            
            # Buscar solicitações do funcionário
            requests = CreditService.get_credit_requests_by_employee(employee_id)
            logging.info(f"Solicitações encontradas para o funcionário {employee_id}: {len(requests)}")
            
            # Converter para dicionário
            requests_dict = [req.to_dict() for req in requests]
            logging.info(f"Dados das solicitações: {requests_dict}")
            
            return jsonify({
                'message': 'Solicitações encontradas',
                'credit_requests': requests_dict,
                'total': len(requests)
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao buscar solicitações: {str(e)}")
            return jsonify({'message': f'Erro ao buscar solicitações: {str(e)}'}), 500

    @staticmethod
    def get_pending_credit_requests():
        """Lista todas as solicitações de crédito pendentes"""
        try:
            # Buscar todas as solicitações
            all_requests = CreditService.get_all_credit_requests()
            logging.info(f"Total de solicitações encontradas: {len(all_requests)}")
            
            # Filtrar apenas as pendentes
            pending_requests = [req for req in all_requests if req.status == CreditRequestStatus.PENDING]
            logging.info(f"Solicitações pendentes: {len(pending_requests)}")
            
            # Converter para dicionário
            requests_dict = [req.to_dict() for req in pending_requests]
            logging.info(f"Dados das solicitações: {requests_dict}")
            
            return jsonify({
                'message': 'Solicitações pendentes encontradas',
                'credit_requests': requests_dict,
                'total': len(pending_requests)
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao buscar solicitações: {str(e)}")
            return jsonify({'message': f'Erro ao buscar solicitações: {str(e)}'}), 500
