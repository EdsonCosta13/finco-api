from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.models.invitation import EmployeeInvitation
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import uuid
from app.controllers.user_controller import UserController

users_bp = Blueprint('users', __name__)

# Get all users (admin or company manager)
@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['user_id'])
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    if user.is_admin:
        # Admin can see all users
        users = User.query.all()
    elif user.role == 'manager':
        # Manager can see users from their company
        users = User.query.filter_by(company_id=user.company_id).all()
    else:
        return jsonify({'message': 'Acesso não autorizado'}), 403
    
    return jsonify({
        'users': [u.to_dict() for u in users]
    }, 200)

# Get a specific user
@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user['user_id'])
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'message': 'Usuário alvo não encontrado'}), 404
    
    # Check permissions
    if user.is_admin or current_user['user_id'] == user_id or (
        user.role == 'manager' and 
        target_user.company_id == user.company_id
    ):
        return jsonify({'user': target_user.to_dict()}), 200
    
    return jsonify({'message': 'Acesso não autorizado'}), 403

# Update user
@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user['user_id'])
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'message': 'Usuário alvo não encontrado'}), 404
    
    # Check permissions
    if not (user.is_admin or current_user['user_id'] == user_id or (
        user.role == 'manager' and 
        target_user.company_id == user.company_id
    )):
        return jsonify({'message': 'Acesso não autorizado'}), 403
    
    data = request.get_json()
    
    # Fields that can be updated
    if 'name' in data:
        target_user.name = data['name']
    
    # Only admin or self can update email
    if 'email' in data and (user.is_admin or current_user['user_id'] == user_id):
        target_user.email = data['email']
    
    # Only admin or manager can update role
    if 'role' in data and (user.is_admin or (user.role == 'manager' and target_user.company_id == user.company_id)):
        # Managers can only set employees to 'employee' or 'manager'
        if user.is_admin or data['role'] in ['employee', 'manager']:
            target_user.role = data['role']
    
    # Only admin can update admin status
    if 'is_admin' in data and user.is_admin:
        target_user.is_admin = data['is_admin']
    
    # Only admin can update active status
    if 'is_active' in data and (user.is_admin or (
        user.role == 'manager' and 
        target_user.company_id == user.company_id and
        target_user.id != user.id  # Can't deactivate yourself
    )):
        target_user.is_active = data['is_active']
    
    # Update password if provided
    if 'password' in data:
        target_user.set_password(data['password'])
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Usuário atualizado com sucesso',
            'user': target_user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao atualizar usuário: {str(e)}'}), 500

# Delete user
@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user['user_id'])
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'message': 'Usuário alvo não encontrado'}), 404
    
    # Check permissions
    if not (user.is_admin or (
        user.role == 'manager' and 
        target_user.company_id == user.company_id and
        target_user.id != user.id  # Can't delete yourself
    )):
        return jsonify({'message': 'Acesso não autorizado'}), 403
    
    try:
        db.session.delete(target_user)
        db.session.commit()
        return jsonify({'message': 'Usuário excluído com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao excluir usuário: {str(e)}'}), 500

# Invite employee
@users_bp.route('/invite', methods=['POST'])
@jwt_required()
def invite_employee():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['user_id'])
    
    if not user or user.role not in ['manager', 'admin']:
        return jsonify({'message': 'Acesso não autorizado'}), 403
    
    data = request.get_json()
    if not data or not data.get('email') or not data.get('role'):
        return jsonify({'message': 'Email e função são obrigatórios'}), 400
    
    if data['role'] not in ['employee', 'manager']:
        return jsonify({'message': 'Função deve ser "employee" ou "manager"'}), 400
    
    # Check if invitation already exists
    existing_invitation = EmployeeInvitation.query.filter_by(
        email=data['email'],
        company_id=user.company_id,
        is_used=False
    ).first()
    
    if existing_invitation:
        return jsonify({'message': 'Já existe um convite pendente para este email'}), 400
    
    # Create new invitation
    expires_at = datetime.utcnow() + timedelta(days=7)
    invitation_code = str(uuid.uuid4())
    
    invitation = EmployeeInvitation(
        email=data['email'],
        role=data['role'],
        company_id=user.company_id,
        invitation_code=invitation_code,
        expires_at=expires_at,
        created_by=user.id
    )
    
    try:
        db.session.add(invitation)
        db.session.commit()
        
        # Send email with invitation (implement email sending)
        # send_invitation_email(data['email'], invitation_code)
        
        return jsonify({
            'message': 'Convite enviado com sucesso',
            'invitation': {
                'email': invitation.email,
                'role': invitation.role,
                'invitation_code': invitation.invitation_code,
                'expires_at': invitation.expires_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao enviar convite: {str(e)}'}), 500

@users_bp.route('/company/users', methods=['GET'])
@jwt_required()
@User.manager_required
def get_company_users():
    return UserController.get_company_users()