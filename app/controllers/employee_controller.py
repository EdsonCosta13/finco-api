from flask import jsonify, request
from app.services.employee_service import EmployeeService
from app.services.invitation_service import InvitationService
from app.models.invitation import InvitationStatus
import logging

class EmployeeController:
    @staticmethod
    def get_all_employees():
        try:
            employees = EmployeeService.get_all_employees()
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Funcionários encontrados',
                'data': [employee.to_dict() for employee in employees],
                'total': len(employees)
            }), 200
        except Exception as e:
            logging.error(f"Erro ao buscar funcionários: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao buscar funcionários: {str(e)}'
            }), 500
    
    @staticmethod
    def get_employees_by_company(company_id):
        try:
            employees = EmployeeService.get_employees_by_company(company_id)
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Funcionários da empresa encontrados',
                'data': [employee.to_dict() for employee in employees],
                'total': len(employees)
            }), 200
        except Exception as e:
            logging.error(f"Erro ao buscar funcionários da empresa: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao buscar funcionários: {str(e)}'
            }), 500
    
    @staticmethod
    def get_employee_by_id(employee_id):
        try:
            employee = EmployeeService.get_employee_by_id(employee_id)
            if not employee:
                return jsonify({
                    'status': 'error',
                    'statusCode': 404,
                    'message': 'Funcionário não encontrado'
                }), 404
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Funcionário encontrado',
                'data': employee.to_dict()
            }), 200
        except Exception as e:
            logging.error(f"Erro ao buscar funcionário: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao buscar funcionário: {str(e)}'
            }), 500
    
    @staticmethod
    def create_employee():
        try:
            data = request.get_json()
            
            # Basic validation
            required_fields = ['name', 'email', 'cpf', 'salary', 'company_id', 'password', 'invitation_code']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'status': 'error',
                        'statusCode': 400,
                        'message': f'Campo obrigatório não fornecido: {field}'
                    }), 400
            
            # Validate invitation code
            valid, invitation_or_error = InvitationService.validate_employee_invitation(data['invitation_code'])
            if not valid:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': invitation_or_error
                }), 400
            
            # Verify email matches invitation
            if invitation_or_error.email.lower().strip() != data['email'].lower().strip():
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': 'O email não corresponde ao convite'
                }), 400
            
            # Verify company matches invitation
            if invitation_or_error.company_id != data['company_id']:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': 'A empresa não corresponde ao convite'
                }), 400
            
            employee, error = EmployeeService.create_employee(data)
            if error:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': error
                }), 400
            
            # Mark invitation as used
            InvitationService.mark_employee_invitation_used(invitation_or_error)
            
            return jsonify({
                'status': 'success',
                'statusCode': 201,
                'message': 'Funcionário criado com sucesso',
                'data': employee.to_dict()
            }), 201
            
        except Exception as e:
            logging.error(f"Erro ao criar funcionário: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao criar funcionário: {str(e)}'
            }), 500
    
    @staticmethod
    def invite_employee():
        try:
            data = request.get_json()
            
            # Basic validation
            required_fields = ['email', 'company_id']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'status': 'error',
                        'statusCode': 400,
                        'message': f'Campo obrigatório não fornecido: {field}'
                    }), 400
            
            # Optional role field
            role = data.get('role', 'employee')
            
            # Create invitation
            invitation, error = InvitationService.create_employee_invitation(
                email=data['email'],
                company_id=data['company_id'],
                role=role
            )
            
            if error:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': error
                }), 400
            
            return jsonify({
                'status': 'success',
                'statusCode': 201,
                'message': 'Convite enviado com sucesso',
                'data': {
                    'email': invitation.email,
                    'company_id': invitation.company_id,
                    'role': invitation.role,
                    'expires_at': invitation.expires_at.isoformat()
                }
            }), 201
            
        except Exception as e:
            logging.error(f"Erro ao enviar convite: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao enviar convite: {str(e)}'
            }), 500
    
    @staticmethod
    def update_employee(employee_id):
        try:
            data = request.get_json()
            employee, error = EmployeeService.update_employee(employee_id, data)
            
            if error:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': error
                }), 400
            
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Funcionário atualizado com sucesso',
                'data': employee.to_dict()
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao atualizar funcionário: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao atualizar funcionário: {str(e)}'
            }), 500
    
    @staticmethod
    def delete_employee(employee_id):
        try:
            success, error = EmployeeService.delete_employee(employee_id)
            
            if not success:
                return jsonify({
                    'status': 'error',
                    'statusCode': 404,
                    'message': error
                }), 404
            
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Funcionário excluído com sucesso'
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao excluir funcionário: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao excluir funcionário: {str(e)}'
            }), 500
    
    @staticmethod
    def register_employee():
        data = request.get_json()
        
        # Basic validation
        required_fields = ['name', 'email', 'cpf', 'position', 'salary', 'phone', 'password', 'invitation_code']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate invitation code
        valid, invitation_or_error = InvitationService.validate_employee_invitation(data['invitation_code'])
        if not valid:
            return jsonify({"error": invitation_or_error}), 400
        
        # Verify email matches invitation
        if invitation_or_error.email.lower().strip() != data['email'].lower().strip():
            return jsonify({"error": "O email não corresponde ao convite"}), 400
        
        employee, error = EmployeeService.register_employee(data)
        if error:
            return jsonify({"error": error}), 400
        
        # Mark invitation as used
        invitation_or_error.status = InvitationStatus.USED
        
        return jsonify({
            "message": "Funcionário registrado com sucesso",
            "employee": employee.to_dict()
        }), 201
