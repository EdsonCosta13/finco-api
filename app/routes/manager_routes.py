from flask import Blueprint
from app.controllers.credit_controller import CreditController
from app.models.user import User
from flask_jwt_extended import jwt_required

manager_bp = Blueprint('manager_bp', __name__)

# Credit request management routes
@manager_bp.route('/credit/requests', methods=['GET'])
@jwt_required()
@User.manager_required
def get_company_credit_requests():
    """Lista todas as solicitações de crédito da empresa do gerente"""
    return CreditController.get_company_credit_requests()

@manager_bp.route('/credit/requests/pending', methods=['GET'])
@jwt_required()
@User.manager_required
def get_pending_credit_requests():
    """Lista todas as solicitações de crédito pendentes da empresa do gerente"""
    return CreditController.get_pending_credit_requests()

@manager_bp.route('/credit/requests/<int:credit_id>/status', methods=['PUT'])
@jwt_required()
@User.manager_required
def update_credit_request_status(credit_id):
    """Atualiza o status de uma solicitação de crédito"""
    return CreditController.update_credit_status(credit_id) 