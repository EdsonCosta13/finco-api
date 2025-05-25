from flask import Blueprint
from app.controllers.invitation_controller import InvitationController

invitation_bp = Blueprint('invitation_bp', __name__)

# Invitation creation endpoints
invitation_bp.route('/company', methods=['POST'])(InvitationController.create_company_invitation)
invitation_bp.route('/employee', methods=['POST'])(InvitationController.create_employee_invitation)

# Invitation validation endpoint
invitation_bp.route('/validate', methods=['POST'])(InvitationController.validate_invitation)
