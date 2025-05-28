from flask import Blueprint, request, jsonify
from app.controllers.invitation_controller import InvitationController
from flask_jwt_extended import jwt_required
from app.models.user import User

invitation_bp = Blueprint('invitation', __name__)

# Invitation creation endpoints
@invitation_bp.route('/company', methods=['POST'])
def create_company_invitation():
    return InvitationController.create_company_invitation()

@invitation_bp.route('/employee', methods=['POST'])
@jwt_required()
def create_employee_invitation():
    return InvitationController.create_employee_invitation()

# Invitation validation endpoint
@invitation_bp.route('/validate/company/<invitation_code>', methods=['GET'])
def validate_company_invitation(invitation_code):
    return InvitationController.validate_company_invitation(invitation_code)

@invitation_bp.route('/validate/employee/<invitation_code>', methods=['GET'])
def validate_employee_invitation(invitation_code):
    return InvitationController.validate_employee_invitation(invitation_code)

@invitation_bp.route('/company/invitations', methods=['GET'])
@jwt_required()
@User.manager_required
def get_company_invitations():
    return InvitationController.get_company_invitations()
