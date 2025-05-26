from flask import Blueprint
from app.controllers.credit_controller import CreditController
from app.models.user import User
from flask_jwt_extended import jwt_required

credit_bp = Blueprint('credit_bp', __name__)

# Credit CRUD operations
credit_bp.route('/', methods=['GET'])(CreditController.get_all_credit_requests)
credit_bp.route('/<int:credit_id>', methods=['GET'])(CreditController.get_credit_request_by_id)
credit_bp.route('/', methods=['POST'])(CreditController.create_credit_request)
# credit_bp.route('/<int:credit_id>', methods=['PUT'])(CreditController.update_credit_request)
# credit_bp.route('/<int:credit_id>', methods=['DELETE'])(CreditController.delete_credit_request)

# Credit status update
credit_bp.route('/<int:credit_id>/status', methods=['PUT'])(CreditController.update_credit_status)

# Credit relationships
credit_bp.route('/employee/<int:employee_id>', methods=['GET'])(CreditController.get_credit_requests_by_employee)

# Employee credit request
@credit_bp.route('/employee/request', methods=['POST'])
@jwt_required()
@User.employee_required
def create_employee_credit_request():
    """Cria uma nova solicitação de crédito"""
    return CreditController.create_employee_credit_request()

# Rotas para gerentes
@credit_bp.route('/manager/approve/<int:credit_id>', methods=['POST'])
@jwt_required()
@User.manager_required
def approve_credit_request(credit_id):
    """Aprova uma solicitação de crédito"""
    return CreditController.update_credit_status(credit_id, 'approved')

@credit_bp.route('/manager/reject/<int:credit_id>', methods=['POST'])
@jwt_required()
@User.manager_required
def reject_credit_request(credit_id):
    """Rejeita uma solicitação de crédito"""
    return CreditController.update_credit_status(credit_id, 'rejected')

# Rotas para visualização
@credit_bp.route('/employee/requests', methods=['GET'])
@jwt_required()
@User.employee_required
def get_employee_requests():
    """Lista as solicitações de crédito do funcionário"""
    return CreditController.get_employee_credit_requests()

@credit_bp.route('/manager/pending', methods=['GET'])
@jwt_required()
@User.manager_required
def get_pending_requests():
    """Lista as solicitações de crédito pendentes"""
    return CreditController.get_pending_credit_requests()
