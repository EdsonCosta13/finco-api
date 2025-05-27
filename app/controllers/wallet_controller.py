from flask import jsonify, request
from app.services.wallet_service import WalletService
from app.models.wallet_transaction import TransactionType
from app.models.payment import PaymentStatus
from flask_jwt_extended import get_jwt
import logging

class WalletController:
    @staticmethod
    def get_wallet():
        """Retorna a carteira do funcionário"""
        try:
            jwt = get_jwt()
            employee_id = jwt.get('employee_id')
            
            if not employee_id:
                return jsonify({
                    'status': 'error',
                    'statusCode': 401,
                    'message': 'ID do funcionário não encontrado no token'
                }), 401
            
            wallet = WalletService.get_wallet_by_employee(employee_id)
            
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Carteira encontrada',
                'data': wallet.to_dict()
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao buscar carteira: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao buscar carteira: {str(e)}'
            }), 500
    
    @staticmethod
    def deposit():
        """Realiza um depósito na carteira"""
        try:
            data = request.get_json()
            jwt = get_jwt()
            employee_id = jwt.get('employee_id')
            
            if not employee_id:
                return jsonify({
                    'status': 'error',
                    'statusCode': 401,
                    'message': 'ID do funcionário não encontrado no token'
                }), 401
            
            if not data or 'amount' not in data:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': 'Valor do depósito não fornecido'
                }), 400
            
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': 'O valor do depósito deve ser maior que zero'
                }), 400
            
            wallet, transaction = WalletService.deposit(employee_id, amount)
            
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Depósito realizado com sucesso',
                'data': {
                    'wallet': wallet.to_dict(),
                    'transaction': transaction.to_dict()
                }
            }), 200
            
        except ValueError as e:
            return jsonify({
                'status': 'error',
                'statusCode': 400,
                'message': str(e)
            }), 400
        except Exception as e:
            logging.error(f"Erro ao realizar depósito: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao realizar depósito: {str(e)}'
            }), 500
    
    @staticmethod
    def withdraw():
        """Realiza um saque da carteira"""
        try:
            data = request.get_json()
            jwt = get_jwt()
            employee_id = jwt.get('employee_id')
            
            if not employee_id:
                return jsonify({
                    'status': 'error',
                    'statusCode': 401,
                    'message': 'ID do funcionário não encontrado no token'
                }), 401
            
            if not data or 'amount' not in data:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': 'Valor do saque não fornecido'
                }), 400
            
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': 'O valor do saque deve ser maior que zero'
                }), 400
            
            wallet, transaction = WalletService.withdraw(employee_id, amount)
            
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Saque realizado com sucesso',
                'data': {
                    'wallet': wallet.to_dict(),
                    'transaction': transaction.to_dict()
                }
            }), 200
            
        except ValueError as e:
            return jsonify({
                'status': 'error',
                'statusCode': 400,
                'message': str(e)
            }), 400
        except Exception as e:
            logging.error(f"Erro ao realizar saque: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao realizar saque: {str(e)}'
            }), 500
    
    @staticmethod
    def get_transactions():
        """Retorna as transações da carteira"""
        try:
            jwt = get_jwt()
            employee_id = jwt.get('employee_id')
            
            if not employee_id:
                return jsonify({
                    'status': 'error',
                    'statusCode': 401,
                    'message': 'ID do funcionário não encontrado no token'
                }), 401
            
            # Obtém o tipo de transação do query parameter, se fornecido
            transaction_type = request.args.get('type')
            if transaction_type and transaction_type not in [t.value for t in TransactionType]:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': 'Tipo de transação inválido'
                }), 400
            
            transactions = WalletService.get_transactions(employee_id, transaction_type)
            
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Transações encontradas',
                'data': [t.to_dict() for t in transactions],
                'total': len(transactions)
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao buscar transações: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao buscar transações: {str(e)}'
            }), 500
    
    @staticmethod
    def get_payments():
        """Retorna os pagamentos de dividendos/juros"""
        try:
            jwt = get_jwt()
            employee_id = jwt.get('employee_id')
            
            if not employee_id:
                return jsonify({
                    'status': 'error',
                    'statusCode': 401,
                    'message': 'ID do funcionário não encontrado no token'
                }), 401
            
            # Obtém o status do pagamento do query parameter, se fornecido
            status = request.args.get('status')
            if status and status not in [s.value for s in PaymentStatus]:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': 'Status de pagamento inválido'
                }), 400
            
            payments = WalletService.get_payments(employee_id, status)
            
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Pagamentos encontrados',
                'data': [p.to_dict() for p in payments],
                'total': len(payments)
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao buscar pagamentos: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao buscar pagamentos: {str(e)}'
            }), 500 