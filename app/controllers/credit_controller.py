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
    def update_credit_status(credit_id, status=None):
        """Atualiza o status de uma solicitação de crédito"""
        try:
            # Se o status não for fornecido, tenta obter do corpo da requisição
            if status is None:
                data = request.get_json()
                if not data or 'status' not in data:
                    return jsonify({'message': 'Status não fornecido'}), 400
                status = data['status']
            
            # Valida o status
            valid_statuses = ['approved', 'rejected']
            if status not in valid_statuses:
                return jsonify({'message': f'Status inválido. Deve ser um dos seguintes: {", ".join(valid_statuses)}'}), 400
            
            jwt = get_jwt()
            company_id = jwt.get('company_id')
            
            if not company_id:
                return jsonify({'message': 'ID da empresa não encontrado no token'}), 401
            
            result, error = CreditService.update_credit_request_status(credit_id, status, company_id)
            
            if error:
                return jsonify({'message': error}), 400
                
            return jsonify({
                'message': f'Solicitação de crédito {status} com sucesso',
                'credit_request': result.to_dict()
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao atualizar status: {str(e)}")
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
        """Lista todas as solicitações de crédito pendentes da empresa do gerente"""
        try:
            jwt = get_jwt()
            company_id = jwt.get('company_id')
            
            if not company_id:
                return jsonify({'message': 'ID da empresa não encontrado no token'}), 401
            
            # Buscar solicitações pendentes da empresa
            requests = CreditService.get_pending_credit_requests_by_company(company_id)
            logging.info(f"Solicitações pendentes encontradas para a empresa {company_id}: {len(requests)}")
            
            # Converter para dicionário
            requests_dict = [req.to_dict() for req in requests]
            logging.info(f"Dados das solicitações: {requests_dict}")
            
            return jsonify({
                'message': 'Solicitações pendentes encontradas',
                'credit_requests': requests_dict,
                'total': len(requests)
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao buscar solicitações: {str(e)}")
            return jsonify({'message': f'Erro ao buscar solicitações: {str(e)}'}), 500

    @staticmethod
    def get_company_credit_requests():
        """Lista todas as solicitações de crédito da empresa do gerente, opcionalmente filtradas por status"""
        try:
            jwt = get_jwt()
            company_id = jwt.get('company_id')
            
            if not company_id:
                return jsonify({'message': 'ID da empresa não encontrado no token'}), 401
            
            # Obter status do query parameter, se fornecido
            status = request.args.get('status')
            
            # Validar status se fornecido
            if status and status not in ['pending', 'approved', 'rejected']:
                return jsonify({'message': 'Status inválido. Deve ser um dos seguintes: pending, approved, rejected'}), 400
            
            # Buscar solicitações da empresa
            requests = CreditService.get_credit_requests_by_company_and_status(company_id, status)
            logging.info(f"Solicitações encontradas para a empresa {company_id}: {len(requests)}")
            
            # Converter para dicionário
            requests_dict = [req.to_dict() for req in requests]
            
            return jsonify({
                'message': 'Solicitações encontradas',
                'credit_requests': requests_dict,
                'total': len(requests),
                'status_filter': status
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao buscar solicitações: {str(e)}")
            return jsonify({'message': f'Erro ao buscar solicitações: {str(e)}'}), 500
