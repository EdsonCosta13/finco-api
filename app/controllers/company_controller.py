from flask import jsonify, request
from app.services.company_service import CompanyService
from app.services.invitation_service import InvitationService
import logging

class CompanyController:
    @staticmethod
    def get_all_companies():
        try:
            companies = CompanyService.get_all_companies()
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Empresas encontradas',
                'data': [company.to_dict() for company in companies],
                'total': len(companies)
            }), 200
        except Exception as e:
            logging.error(f"Erro ao buscar empresas: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao buscar empresas: {str(e)}'
            }), 500
    
    @staticmethod
    def get_company_by_id(company_id):
        try:
            company = CompanyService.get_company_by_id(company_id)
            if not company:
                return jsonify({
                    'status': 'error',
                    'statusCode': 404,
                    'message': 'Empresa não encontrada'
                }), 404
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Empresa encontrada',
                'data': company.to_dict()
            }), 200
        except Exception as e:
            logging.error(f"Erro ao buscar empresa: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao buscar empresa: {str(e)}'
            }), 500
    
    @staticmethod
    def create_company():
        try:
            data = request.get_json()
            
            # Basic validation
            required_fields = ['name', 'nif', 'email', 'invitation_code']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'status': 'error',
                        'statusCode': 400,
                        'message': f'Campo obrigatório não fornecido: {field}'
                    }), 400
            
            # Validate manager data
            if 'manager' not in data:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': 'Informações do gerente são obrigatórias'
                }), 400
            
            manager_data = data['manager']
            required_manager_fields = ['name', 'email', 'password']
            for field in required_manager_fields:
                if field not in manager_data:
                    return jsonify({
                        'status': 'error',
                        'statusCode': 400,
                        'message': f'Campo obrigatório do gerente não fornecido: {field}'
                    }), 400
            
            # Validate the invitation code before creating the company
            invitation_code = data['invitation_code']
            valid, result = InvitationService.validate_company_invitation(invitation_code)
            
            if not valid:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': 'Código de convite inválido ou expirado'
                }), 400
                
            # Include the validated invitation in the data
            data['invitation'] = result
            
            company, error = CompanyService.create_company(data)
            if error:
                if "nif already exists" in error.lower():
                    return jsonify({
                        'status': 'error',
                        'statusCode': 400,
                        'message': 'Este NIF já está registrado no sistema'
                    }), 400
                elif "email already exists" in error.lower():
                    return jsonify({
                        'status': 'error',
                        'statusCode': 400,
                        'message': 'Este email já está registrado no sistema'
                    }), 400
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': f'Erro ao registrar: {error}'
                }), 400
            
            # Mark invitation as used only after successful company creation
            InvitationService.mark_company_invitation_used(result)
            
            return jsonify({
                'status': 'success',
                'statusCode': 201,
                'message': 'Empresa criada com sucesso',
                'data': company.to_dict()
            }), 201
            
        except Exception as e:
            logging.error(f"Erro ao criar empresa: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao criar empresa: {str(e)}'
            }), 500
    
    @staticmethod
    def update_company(company_id):
        try:
            data = request.get_json()
            company, error = CompanyService.update_company(company_id, data)
            
            if error:
                return jsonify({
                    'status': 'error',
                    'statusCode': 400,
                    'message': error
                }), 400
            
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Empresa atualizada com sucesso',
                'data': company.to_dict()
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao atualizar empresa: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao atualizar empresa: {str(e)}'
            }), 500
    
    @staticmethod
    def delete_company(company_id):
        try:
            success, error = CompanyService.delete_company(company_id)
            
            if not success:
                return jsonify({
                    'status': 'error',
                    'statusCode': 404,
                    'message': error
                }), 404
            
            return jsonify({
                'status': 'success',
                'statusCode': 200,
                'message': 'Empresa excluída com sucesso'
            }), 200
            
        except Exception as e:
            logging.error(f"Erro ao excluir empresa: {str(e)}")
            return jsonify({
                'status': 'error',
                'statusCode': 500,
                'message': f'Erro ao excluir empresa: {str(e)}'
            }), 500
