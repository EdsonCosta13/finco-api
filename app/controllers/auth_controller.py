from flask import jsonify, request
from app import db
from app.models.user import User
from app.models.employee import Employee
from flask_jwt_extended import create_access_token, get_jwt_identity
from datetime import timedelta
import logging

class AuthController:
    @staticmethod
    def login():
        try:
            data = request.get_json()
            
            if not data or not data.get('email') or not data.get('password'):
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': 'Email e senha são obrigatórios'
                }), 400
            
            user = User.query.filter_by(email=data['email']).first()
            
            if not user or not user.check_password(data['password']):
                return jsonify({
                    'status': 'error',
                    'statusCode': 401,
                    'message': 'Email ou senha inválidos'
                }), 401
            
            if not user.is_active:
                return jsonify({
                    'status': 'error',
                    'statusCode': 401,
                    'message': 'Conta desativada. Entre em contato com o administrador.'
                }), 401
            
            # Generate token
            access_token = create_access_token(
                identity={'user_id': user.id, 'role': user.role, 'company_id': user.company_id},
                expires_delta=timedelta(hours=24)
            )
            
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Login realizado com sucesso',
                'data': {
                    'access_token': access_token,
                    'user': user.to_dict()
                }
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao realizar login: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao realizar login: {str(e)}'
            }), 500

    @staticmethod
    def employee_login():
        try:
            data = request.get_json()
            
            if not data or not data.get('email') or not data.get('password'):
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': 'Email e senha são obrigatórios'
                }), 400
                
            user = User.query.filter_by(email=data['email']).first()
            
            if not user or not user.check_password(data['password']):
                return jsonify({
                    'status': 'error',
                    'statusCode': 401,
                    'message': 'Email ou senha inválidos'
                }), 401
                
            if not user.is_active:
                return jsonify({
                    'status': 'error',
                    'statusCode': 401,
                    'message': 'Conta desativada. Entre em contato com o administrador.'
                }), 401
            
            if not user.is_employee():
                return jsonify({
                    'status': 'error',
                    'statusCode': 403,
                    'message': 'Acesso permitido apenas para funcionários'
                }), 403
            
            # Get employee details
            employee = Employee.query.filter_by(email=user.email).first()
            if not employee:
                return jsonify({
                    'status': 'error',
                    'statusCode': 404,
                    'message': 'Dados do funcionário não encontrados'
                }), 404
            
            # Generate token with user ID as identity and role in claims
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={
                    'role': 'employee',
                    'employee_id': employee.id,
                    'company_id': user.company_id
                }
            )
            
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Login realizado com sucesso',
                'data': {
                    'access_token': access_token,
                    'user': user.to_dict(),
                    'employee': employee.to_dict()
                }
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao realizar login do funcionário: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao realizar login: {str(e)}'
            }), 500
    
    @staticmethod
    def verify_employee():
        try:
            current_user = get_jwt_identity()
            user = User.query.get(current_user['user_id'])
            employee = Employee.query.filter_by(email=user.email).first()
            
            if not employee:
                return jsonify({
                    'status': 'error',
                    'statusCode': 404,
                    'message': 'Dados do funcionário não encontrados'
                }), 404
            
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Token válido',
                'data': {
                    'user': user.to_dict(),
                    'employee': employee.to_dict()
                }
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao verificar funcionário: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao verificar funcionário: {str(e)}'
            }), 500

    @staticmethod
    def get_current_user():
        try:
            current_user = get_jwt_identity()
            # Handle both string and dictionary identity formats
            user_id = current_user['user_id'] if isinstance(current_user, dict) else current_user
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({
                    'status': 'error',
                    'statusCode': 404,
                    'message': 'Usuário não encontrado'
                }), 404
            
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Dados do usuário recuperados com sucesso',
                'data': {
                    'user': user.to_dict()
                }
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao recuperar dados do usuário: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao recuperar dados do usuário: {str(e)}'
            }), 500 