from flask import Blueprint
from app.controllers.investment_controller import InvestmentController

investment_bp = Blueprint('investment_bp', __name__)

# Investment CRUD operations
investment_bp.route('/', methods=['GET'])(InvestmentController.get_all_investments)
investment_bp.route('/<int:investment_id>', methods=['GET'])(InvestmentController.get_investment_by_id)
investment_bp.route('/', methods=['POST'])(InvestmentController.create_investment)
# investment_bp.route('/<int:investment_id>', methods=['PUT'])(InvestmentController.update_investment)
# investment_bp.route('/<int:investment_id>', methods=['DELETE'])(InvestmentController.delete_investment)

# Investment relationships
investment_bp.route('/employee/<int:employee_id>', methods=['GET'])(InvestmentController.get_investments_by_employee)
investment_bp.route('/credit/<int:credit_id>', methods=['GET'])(InvestmentController.get_investments_by_credit)
