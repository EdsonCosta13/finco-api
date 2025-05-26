from flask import Blueprint
from app.controllers.employee_controller import EmployeeController
from app.controllers.investment_controller import InvestmentController
from app.controllers.credit_controller import CreditController

employee_bp = Blueprint('employee_bp', __name__)

# Employee CRUD operations
employee_bp.route('/', methods=['GET'])(EmployeeController.get_all_employees)
employee_bp.route('/<int:employee_id>', methods=['GET'])(EmployeeController.get_employee_by_id)
employee_bp.route('/', methods=['POST'])(EmployeeController.create_employee)
employee_bp.route('/<int:employee_id>', methods=['PUT'])(EmployeeController.update_employee)
employee_bp.route('/<int:employee_id>', methods=['DELETE'])(EmployeeController.delete_employee)

# Employee invitation
employee_bp.route('/invite', methods=['POST'])(EmployeeController.invite_employee)

# Employee's investments
employee_bp.route('/<int:employee_id>/investments', methods=['GET'])(InvestmentController.get_investments_by_employee)
employee_bp.route('/<int:employee_id>/investments', methods=['POST'])(InvestmentController.create_investment)

# Employee's credit requests
employee_bp.route('/<int:employee_id>/credits', methods=['GET'])(CreditController.get_credit_requests_by_employee)
employee_bp.route('/<int:employee_id>/credits', methods=['POST'])(CreditController.create_credit_request)

# Employee registration
employee_bp.route('/register', methods=['POST'])(EmployeeController.register_employee)
