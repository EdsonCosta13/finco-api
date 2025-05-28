from flask import jsonify, request
from app.services.invitation_service import InvitationService
from app.models.invitation import InvitationStatus
from app.models.company import Company
from flask_jwt_extended import get_jwt
import logging

class InvitationController:
    @staticmethod
    def create_company_invitation():
        try:
            data = request.get_json()
            
            # Basic validation
            if 'email' not in data:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': 'Campo obrigatório não fornecido: email'
                }), 400
            
            # Create invitation
            invitation, error = InvitationService.create_company_invitation(
                email=data['email']
            )
            
            if error:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': error
                }), 400
            
            return jsonify({
                'status': 'success',
                'statusCode': 201,
                'message': 'Convite para empresa criado com sucesso',
                'data': {
                    'email': invitation.email,
                    'expires_at': invitation.expires_at.isoformat()
                }
            }), 201
            
        except Exception as e:
            logging.error(f"Erro ao criar convite para empresa: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao criar convite: {str(e)}'
            }), 500
    
    @staticmethod
    def create_employee_invitation():
        try:
            data = request.get_json()
            
            # Basic validation
            required_fields = ['email', 'company_id']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'status': 'error',
                        'statusCode': 400,
                        'message': f'Campo obrigatório não fornecido: {field}'
                    }), 400
            
            # Optional role field
            role = data.get('role', 'employee')
            
            # Create invitation
            invitation, error = InvitationService.create_employee_invitation(
                email=data['email'],
                company_id=data['company_id'],
                role=role
            )
            
            if error:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': error
                }), 400
            
            return jsonify({
                'status': 'success',
                'statusCode': 201,
                'message': 'Convite para funcionário criado com sucesso',
                'data': {
                    'email': invitation.email,
                    'company_id': invitation.company_id,
                    'role': invitation.role,
                    'expires_at': invitation.expires_at.isoformat()
                }
            }), 201
            
        except Exception as e:
            logging.error(f"Erro ao criar convite para funcionário: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao criar convite: {str(e)}'
            }), 500
    
    @staticmethod
    def validate_invitation():
        try:
            data = request.get_json()
            
            if not data or 'code' not in data:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': 'Código do convite não fornecido'
                }), 400
            
            # Validate invitation
            valid, invitation_or_error = InvitationService.validate_invitation(data['code'])
            
            if not valid:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': invitation_or_error
                }), 400
            
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Convite válido',
                'data': {
                    'email': invitation_or_error.email,
                    'company_id': invitation_or_error.company_id,
                    'company_name': invitation_or_error.company_name,
                    'role': invitation_or_error.role,
                    'expires_at': invitation_or_error.expires_at.isoformat()
                }
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao validar convite: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao validar convite: {str(e)}'
            }), 500

    @staticmethod
    def get_company_invitations():
        """Lista todos os convites da empresa do gerente"""
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
            
            # Get status filter from query parameters
            status = request.args.get('status')
            
            # Validate status if provided
            if status and status not in ['pending', 'used', 'expired']:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': 'Status inválido. Deve ser um dos seguintes: pending, used, expired'
                }), 400
            
            # Get invitations
            invitations = InvitationService.get_company_invitations(company_id, status)
            
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Convites encontrados com sucesso',
                'data': [invitation.to_dict() for invitation in invitations],
                'total': len(invitations)
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao buscar convites: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao buscar convites: {str(e)}'
            }), 500
