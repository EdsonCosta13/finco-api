from flask import Blueprint
from app.controllers.company_controller import CompanyController
from app.controllers.employee_controller import EmployeeController

company_bp = Blueprint('company_bp', __name__)

# Company CRUD operations
company_bp.route('/', methods=['GET'])(CompanyController.get_all_companies)
company_bp.route('/<int:company_id>', methods=['GET'])(CompanyController.get_company_by_id)
company_bp.route('/', methods=['POST'])(CompanyController.create_company)
company_bp.route('/<int:company_id>', methods=['PUT'])(CompanyController.update_company)
company_bp.route('/<int:company_id>', methods=['DELETE'])(CompanyController.delete_company)

# Employee operations related to company
company_bp.route('/<int:company_id>/employees', methods=['GET'])(EmployeeController.get_employees_by_company)
company_bp.route('/<int:company_id>/employees', methods=['POST'])(EmployeeController.create_employee)
