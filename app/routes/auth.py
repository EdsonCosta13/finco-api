from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.models.invitation import CompanyInvitation, EmployeeInvitation
from app.models.company import Company
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import datetime
from sqlalchemy.exc import IntegrityError
from app.services.invitation_service import InvitationService
from app.models.employee import Employee
from app.models.invitation import InvitationStatus

auth_bp = Blueprint('auth', __name__)

# Endpoints de autenticação geral
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email e senha são obrigatórios'}), 400
        
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Email ou senha inválidos'}), 401
        
    if not user.is_active:
        return jsonify({'message': 'Conta desativada. Entre em contato com o administrador.'}), 401
    
    # Generate token
    access_token = create_access_token(
        identity={'user_id': user.id, 'role': user.role, 'company_id': user.company_id},
        expires_delta=timedelta(hours=24)
    )
    
    return jsonify({
        'message': 'Login realizado com sucesso',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

# Endpoints específicos para funcionários
@auth_bp.route('/employee/login', methods=['POST'])
def employee_login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email e senha são obrigatórios'}), 400
        
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Email ou senha inválidos'}), 401
        
    if not user.is_active:
        return jsonify({'message': 'Conta desativada. Entre em contato com o administrador.'}), 401
    
    if not user.is_employee():
        return jsonify({'message': 'Acesso permitido apenas para funcionários'}), 403
    
    # Get employee details
    employee = Employee.query.filter_by(email=user.email).first()
    if not employee:
        return jsonify({'message': 'Dados do funcionário não encontrados'}), 404
    
    # Generate token
    access_token = create_access_token(
        identity={
            'user_id': user.id,
            'employee_id': employee.id,
            'role': user.role,
            'company_id': user.company_id
        },
        expires_delta=timedelta(hours=24)
    )
    
    return jsonify({
        'message': 'Login realizado com sucesso',
        'access_token': access_token,
        'user': user.to_dict(),
        'employee': employee.to_dict()
    }), 200

@auth_bp.route('/employee/verify', methods=['GET'])
@jwt_required()
@User.employee_required
def verify_employee():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['user_id'])
    employee = Employee.query.filter_by(email=user.email).first()
    
    if not employee:
        return jsonify({'message': 'Dados do funcionário não encontrados'}), 404
    
    return jsonify({
        'message': 'Token válido',
        'user': user.to_dict(),
        'employee': employee.to_dict()
    }), 200

# Endpoints específicos para gerentes
@auth_bp.route('/manager/login', methods=['POST'])
def manager_login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email e senha são obrigatórios'}), 400
        
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Email ou senha inválidos'}), 401
        
    if not user.is_active:
        return jsonify({'message': 'Conta desativada. Entre em contato com o administrador.'}), 401
    
    if not user.is_manager():
        return jsonify({'message': 'Acesso permitido apenas para gerentes'}), 403
    
    # Get company details
    company = Company.query.get(user.company_id)
    if not company:
        return jsonify({'message': 'Dados da empresa não encontrados'}), 404
    
    # Generate token
    access_token = create_access_token(
        identity={
            'user_id': user.id,
            'role': user.role,
            'company_id': user.company_id
        },
        expires_delta=timedelta(hours=24)
    )
    
    return jsonify({
        'message': 'Login realizado com sucesso',
        'access_token': access_token,
        'user': user.to_dict(),
        'company': company.to_dict()
    }), 200

@auth_bp.route('/manager/verify', methods=['GET'])
@jwt_required()
@User.manager_required
def verify_manager():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['user_id'])
    company = Company.query.get(user.company_id)
    
    if not company:
        return jsonify({'message': 'Dados da empresa não encontrados'}), 404
    
    return jsonify({
        'message': 'Token válido',
        'user': user.to_dict(),
        'company': company.to_dict()
    }), 200

# Endpoints de registro
@auth_bp.route('/signup/company', methods=['POST'])
def company_signup():
    data = request.get_json()

    # Validação dos campos principais
    required_fields = ['name', 'email', 'nif', 'invitation_code', 'manager']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'O campo {field} é obrigatório'}), 400

    # Validação dos campos do gerente
    manager_data = data['manager']
    required_manager_fields = ['name', 'email', 'password']
    for field in required_manager_fields:
        if field not in manager_data:
            return jsonify({'message': f'O campo {field} do gerente é obrigatório'}), 400

    # Verify invitation code
    invitation = CompanyInvitation.query.filter_by(
        invitation_code=data['invitation_code'],
        is_used=False
    ).first()

    if not invitation:
        return jsonify({'message': 'Código de convite inválido ou expirado'}), 400

    if invitation.expires_at < datetime.datetime.utcnow():
        return jsonify({'message': 'Código de convite expirado'}), 400

    # Checar se o email do convite é igual ao da empresa ou do gerente
    invitation_email = invitation.email.lower().strip()
    company_email = data.get('email', '').lower().strip()
    manager_email = data['manager'].get('email', '').lower().strip()

    if invitation_email != company_email and invitation_email != manager_email:
        return jsonify({'message': 'O email não corresponde ao convite'}), 400


    if not invitation:
        return jsonify({'message': 'Código de convite inválido ou expirado'}), 400
        
    if invitation.expires_at < datetime.datetime.utcnow():
        return jsonify({'message': 'Código de convite expirado'}), 400

    # Create company
    company = Company(
        name=data['name'],
        nif=data['nif'],
        email=data['email'],
        address=data.get('address', ''),
        phone=data.get('phone', '')
    )

    # Create manager user
    user = User(
        name=manager_data['name'],
        email=manager_data['email'],
        password=manager_data['password'],
        role='manager',
        is_admin=False
    )

    try:
        db.session.add(company)
        db.session.flush()  # Get company ID without committing

        user.company_id = company.id
        db.session.add(user)

        # Update invitation status
        invitation.is_used = True
        invitation.company_id = company.id

        db.session.commit()

        # Generate token
        access_token = create_access_token(
            identity={'user_id': user.id, 'role': user.role, 'company_id': user.company_id},
            expires_delta=timedelta(hours=24)
        )

        return jsonify({
            'message': 'Registro realizado com sucesso',
            'access_token': access_token,
            'user': user.to_dict(),
            'company': company.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao registrar: {str(e)}'}), 500

@auth_bp.route('/signup/employee', methods=['POST'])
def employee_signup():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'email', 'password', 'invitation_code', 'cpf', 'position', 'salary', 'phone']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'O campo {field} é obrigatório'}), 400
    
    # Verify invitation code
    valid, invitation_or_error = InvitationService.validate_employee_invitation(data['invitation_code'])
    if not valid:
        return jsonify({'message': invitation_or_error}), 400
        
    # Verify email matches invitation
    if invitation_or_error.email.lower() != data['email'].lower():
        return jsonify({'message': 'O email não corresponde ao convite'}), 400
    
    if invitation_or_error.expires_at < datetime.datetime.utcnow():
        return jsonify({'message': 'Código de convite expirado'}), 400
    
    try:
        # Create user record for authentication
        user = User(
            name=data['name'],
            email=data['email'],
            password=data['password'],
            role=invitation_or_error.role,  # 'employee' or 'manager'
            company_id=invitation_or_error.company_id,
            is_admin=False
        )
        db.session.add(user)
        db.session.flush()  # Get user ID without committing
        
        # Create employee record with detailed information
        employee = Employee(
            name=data['name'],
            email=data['email'],
            cpf=data['cpf'],
            position=data['position'],
            salary=float(data['salary']),
            phone=data['phone'],
            company_id=invitation_or_error.company_id
        )
        employee.password = data['password']  # This uses the password setter in the model
        db.session.add(employee)
        
        # Update invitation status
        invitation_or_error.is_used = True
        invitation_or_error.status = InvitationStatus.USED
        invitation_or_error.user_id = user.id
        
        db.session.commit()
        
        # Generate token
        access_token = create_access_token(
            identity={'user_id': user.id, 'employee_id': employee.id, 'role': user.role, 'company_id': user.company_id},
            expires_delta=timedelta(hours=24)
        )
        
        return jsonify({
            'message': 'Registro realizado com sucesso',
            'access_token': access_token,
            'user': user.to_dict(),
            'employee': employee.to_dict()
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        error_message = str(e)
        if 'cpf' in error_message.lower():
            return jsonify({'message': 'Este CPF já está registrado'}), 400
        if 'email' in error_message.lower():
            return jsonify({'message': 'Este email já está registrado'}), 400
        return jsonify({'message': f'Erro ao registrar: {error_message}'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao registrar: {str(e)}'}), 500