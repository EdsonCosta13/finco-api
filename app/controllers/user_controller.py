from flask import jsonify, request
from app.models.user import User
from app.models.company import Company
from flask_jwt_extended import get_jwt
import logging

class UserController:
    @staticmethod
    def get_company_users():
        """Lista todos os usuários da empresa do gerente"""
        try:
            jwt = get_jwt()
            company_id = jwt.get('company_id')
            role = jwt.get('role')
            
            if not company_id:
                return jsonify({
                    'status': 'error',
                    'statusCode': 401,
                    'message': 'ID da empresa não encontrado no token'
                }), 401
            
            # Verifica se o usuário tem a role de manager
            if role != 'manager':
                return jsonify({
                    'status': 'error',
                    'statusCode': 403,
                    'message': 'Acesso permitido apenas para gerentes'
                }), 403
            
            # Busca todos os usuários da empresa
            users = User.query.filter_by(company_id=company_id).all()
            
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Usuários encontrados com sucesso',
                'data': [user.to_dict() for user in users],
                'total': len(users)
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao buscar usuários: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao buscar usuários: {str(e)}'
            }), 500 