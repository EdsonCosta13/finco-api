from flask import Blueprint
from app.controllers.investment_controller import InvestmentController
from flask_jwt_extended import jwt_required, get_jwt
from app.models.user import User

investment_bp = Blueprint('investment_bp', __name__)

# Listar todas as oportunidades de investimento
@investment_bp.route('/opportunities', methods=['GET'])
@jwt_required()
@User.employee_required
def list_opportunities():
    """Lista todas as oportunidades de investimento disponíveis"""
    return InvestmentController.list_investment_opportunities()

# Criar um novo investimento
@investment_bp.route('/create', methods=['POST'])
@jwt_required()
@User.employee_required
def create_investment():
    """Cria um novo investimento"""
    return InvestmentController.create_investment()

# Listar investimentos do funcionário
@investment_bp.route('/my-investments', methods=['GET'])
@jwt_required()
@User.employee_required
def get_my_investments():
    """Lista todos os investimentos do funcionário logado"""
    jwt = get_jwt()
    employee_id = jwt.get('employee_id')
    return InvestmentController.get_investments_by_employee(employee_id)

# Buscar investimento por ID
@investment_bp.route('/<int:investment_id>', methods=['GET'])
@jwt_required()
@User.employee_required
def get_investment_by_id(investment_id):
    """Busca um investimento específico por ID"""
    return InvestmentController.get_investment_by_id(investment_id)

# Buscar investimentos por solicitação de crédito
@investment_bp.route('/credit/<int:credit_id>', methods=['GET'])
@jwt_required()
@User.employee_required
def get_investments_by_credit(credit_id):
    """Lista todos os investimentos de uma solicitação de crédito"""
    return InvestmentController.get_investments_by_credit(credit_id)
