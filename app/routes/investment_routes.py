from flask import Blueprint
from app.controllers.investment_controller import InvestmentController
from flask_jwt_extended import jwt_required
from app.models.user import User

investment_bp = Blueprint('investment', __name__)

# Listar todas as oportunidades de investimento
@investment_bp.route('/opportunities', methods=['GET'])
@jwt_required()
def list_opportunities():
    """Lista todas as oportunidades de investimento disponíveis"""
    return InvestmentController.list_investment_opportunities()

# Criar um novo investimento
@investment_bp.route('/create', methods=['POST'])
@jwt_required()
def create_investment():
    """Cria um novo investimento"""
    return InvestmentController.create_investment()

# Listar todos os investimentos
@investment_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_investments():
    """Lista todos os investimentos"""
    return InvestmentController.get_all_investments()

# Buscar investimento por ID
@investment_bp.route('/<int:investment_id>', methods=['GET'])
@jwt_required()
def get_investment_by_id(investment_id):
    """Busca um investimento específico por ID"""
    return InvestmentController.get_investment_by_id(investment_id)

# Buscar investimentos por funcionário
@investment_bp.route('/employee/<int:employee_id>', methods=['GET'])
@jwt_required()
def get_investments_by_employee(employee_id):
    """Lista todos os investimentos de um funcionário"""
    return InvestmentController.get_investments_by_employee(employee_id)

# Buscar investimentos por solicitação de crédito
@investment_bp.route('/credit/<int:credit_id>', methods=['GET'])
@jwt_required()
def get_investments_by_credit(credit_id):
    """Lista todos os investimentos de uma solicitação de crédito"""
    return InvestmentController.get_investments_by_credit(credit_id)
