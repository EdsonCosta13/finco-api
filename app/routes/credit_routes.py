from flask import Blueprint
from app.controllers.credit_controller import CreditController
from app.models.user import User
from flask_jwt_extended import jwt_required

credit_bp = Blueprint('credit_bp', __name__)

# Credit CRUD operations
credit_bp.route('/', methods=['GET'])(CreditController.get_all_credit_requests)
credit_bp.route('/<int:credit_id>', methods=['GET'])(CreditController.get_credit_request_by_id)
credit_bp.route('/', methods=['POST'])(CreditController.create_credit_request)

# Employee credit request routes
@credit_bp.route('/employee/requests', methods=['GET'])
@jwt_required()
@User.employee_required
def get_employee_credit_requests():
    """Lista as solicitações de crédito do funcionário"""
    return CreditController.get_employee_credit_requests()

@credit_bp.route('/employee/requests', methods=['POST'])
@jwt_required()
@User.employee_required
def create_employee_credit_request():
    """Cria uma nova solicitação de crédito"""
    return CreditController.create_employee_credit_request()

@credit_bp.route('/employee/available', methods=['GET'])
@jwt_required()
@User.employee_required
def get_available_credit_requests():
    """Lista todas as solicitações de crédito aprovadas disponíveis para investimento"""
    return CreditController.get_available_credit_requests()

# Manager credit request routes
@credit_bp.route('/manager/pending', methods=['GET'])
@jwt_required()
@User.manager_required
def get_pending_requests():
    """Lista as solicitações de crédito pendentes"""
    return CreditController.get_pending_credit_requests()

@credit_bp.route('/manager/requests', methods=['GET'])
@jwt_required()
@User.manager_required
def get_company_credit_requests():
    """Lista todas as solicitações de crédito da empresa do gerente"""
    return CreditController.get_company_credit_requests()

# Credit status update
@credit_bp.route('/<int:credit_id>/status', methods=['PUT'])
@jwt_required()
@User.manager_required
def update_credit_status(credit_id):
    """Atualiza o status de uma solicitação de crédito"""
    return CreditController.update_credit_status(credit_id)
