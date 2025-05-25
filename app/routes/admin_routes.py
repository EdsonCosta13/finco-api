from flask import Blueprint
from app.controllers.company_controller import CompanyController
from app.controllers.employee_controller import EmployeeController
from app.controllers.credit_controller import CreditController
from app.controllers.investment_controller import InvestmentController

admin_bp = Blueprint('admin_bp', __name__)

# Admin company routes
admin_bp.route('/companies', methods=['GET'])(CompanyController.get_all_companies)
admin_bp.route('/companies/<int:company_id>', methods=['GET'])(CompanyController.get_company_by_id)
admin_bp.route('/companies', methods=['POST'])(CompanyController.create_company)
admin_bp.route('/companies/<int:company_id>', methods=['PUT'])(CompanyController.update_company)
admin_bp.route('/companies/<int:company_id>', methods=['DELETE'])(CompanyController.delete_company)

# Admin employee routes
admin_bp.route('/employees', methods=['GET'])(EmployeeController.get_all_employees)
admin_bp.route('/employees/<int:employee_id>', methods=['GET'])(EmployeeController.get_employee_by_id)
admin_bp.route('/employees', methods=['POST'])(EmployeeController.create_employee)
admin_bp.route('/employees/<int:employee_id>', methods=['PUT'])(EmployeeController.update_employee)
admin_bp.route('/employees/<int:employee_id>', methods=['DELETE'])(EmployeeController.delete_employee)

# Admin credit routes
admin_bp.route('/credits', methods=['GET'])(CreditController.get_all_credit_requests)
admin_bp.route('/credits/<int:credit_id>', methods=['GET'])(CreditController.get_credit_request_by_id)
admin_bp.route('/credits/<int:credit_id>/status', methods=['PUT'])(CreditController.update_credit_status)

# Admin investment routes
admin_bp.route('/investments', methods=['GET'])(InvestmentController.get_all_investments)
admin_bp.route('/investments/<int:investment_id>', methods=['GET'])(InvestmentController.get_investment_by_id)
