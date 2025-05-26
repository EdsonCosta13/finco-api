from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.models.invitation import CompanyInvitation
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import uuid
from app.services.invitation_service import InvitationService

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/signup', methods=['POST'])
def admin_signup():
    """First admin signup - should be restricted in production"""
    data = request.get_json()
    
    # Check if admin exists
    if User.query.filter_by(is_admin=True).first():
        return jsonify({'message': 'Administrador já existe no sistema'}), 400
    
    # Validate required fields
    required_fields = ['name', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'O campo {field} é obrigatório'}), 400
    
    # Create admin user
    admin = User(
        name=data['name'],
        email=data['email'],
        password=data['password'],
        role='admin',
        is_admin=True
    )
    
    try:
        db.session.add(admin)
        db.session.commit()
        return jsonify({
            'message': 'Administrador registrado com sucesso',
            'user': admin.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao registrar administrador: {str(e)}'}), 500

@admin_bp.route('/invite/company', methods=['POST'])
@jwt_required()
def invite_company():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['user_id'])
    
    if not user or not user.is_admin:
        return jsonify({'message': 'Acesso não autorizado'}), 403
    
    data = request.get_json()
    if not data or not data.get('email'):
        return jsonify({'message': 'Email é obrigatório'}), 400
    
    # Create invitation using the service
    invitation, error = InvitationService.create_company_invitation(
        email=data['email'], 
        created_by=user.id
    )
    
    if error:
        return jsonify({'message': f'Erro ao enviar convite: {error}'}), 500
        
    return jsonify({
        'message': 'Convite enviado com sucesso',
        'invitation': invitation.to_dict()
    }), 201