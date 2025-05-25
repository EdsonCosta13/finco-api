from flask import Blueprint
from app.controllers.credit_controller import CreditController

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
