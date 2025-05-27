from flask import Blueprint
from app.controllers.wallet_controller import WalletController
from app.models.user import User
from flask_jwt_extended import jwt_required

wallet_bp = Blueprint('wallet', __name__)

# Rotas da carteira
wallet_bp.route('/wallet', methods=['GET'])(jwt_required()(User.employee_required(WalletController.get_wallet)))
wallet_bp.route('/wallet/deposit', methods=['POST'])(jwt_required()(User.employee_required(WalletController.deposit)))
wallet_bp.route('/wallet/withdraw', methods=['POST'])(jwt_required()(User.employee_required(WalletController.withdraw)))
wallet_bp.route('/wallet/transactions', methods=['GET'])(jwt_required()(User.employee_required(WalletController.get_transactions)))
wallet_bp.route('/wallet/payments', methods=['GET'])(jwt_required()(User.employee_required(WalletController.get_payments))) 