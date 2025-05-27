from app import db
from app.models.investment import Investment
from app.models.employee import Employee
from app.models.credit_request import CreditRequest, CreditRequestStatus
from app.services.credit_service import CreditService
from app.models.user import User
from datetime import datetime
import logging

class InvestmentService:
    # Minimum investment amount
    MIN_INVESTMENT_AMOUNT = 100.0
    
    @staticmethod
    def get_all_investments():
        return Investment.query.all()
    
    @staticmethod
    def get_investments_by_employee(employee_id):
        return Investment.query.filter_by(employee_id=employee_id).all()
    
    @staticmethod
    def get_investments_by_credit(credit_id):
        return Investment.query.filter_by(credit_request_id=credit_id).all()
    
    @staticmethod
    def get_investment_by_id(investment_id):
        return Investment.query.get(investment_id)
    
    @staticmethod
    def get_available_opportunities():
        """Retorna todas as solicitações de crédito disponíveis para investimento"""
        try:
            # Buscar solicitações aprovadas que ainda não foram totalmente financiadas
            opportunities = CreditRequest.query.filter(
                CreditRequest.status == CreditRequestStatus.APPROVED
            ).all()
            
            result = []
            for opp in opportunities:
                # Calcular quanto já foi investido
                invested_amount = sum(inv.amount for inv in opp.investments)
                remaining_amount = opp.amount - invested_amount
                
                if remaining_amount > 0:
                    result.append({
                        'id': opp.id,
                        'employee_name': opp.employee.name,
                        'company_name': opp.employee.company.name,
                        'amount': opp.amount,
                        'remaining_amount': remaining_amount,
                        'term_months': opp.term_months,
                        'interest_rate': opp.interest_rate,
                        'purpose': opp.purpose,
                        'created_at': opp.created_at.isoformat()
                    })
            
            return result
            
        except Exception as e:
            raise Exception(f'Erro ao buscar oportunidades: {str(e)}')
    
    @staticmethod
    def create_investment(employee_id, credit_request_id, amount):
        """Cria um novo investimento"""
        try:
            # Verificar se o funcionário existe
            employee = Employee.query.get(employee_id)
            if not employee:
                return 'Funcionário não encontrado', 404
            
            # Verificar se a solicitação de crédito existe e está aprovada
            credit_request = CreditRequest.query.get(credit_request_id)
            if not credit_request:
                return 'Solicitação de crédito não encontrada', 404
            
            if credit_request.status != CreditRequestStatus.APPROVED:
                return 'A solicitação de crédito não está disponível para investimento', 400
            
            # Verificar se o funcionário não está tentando investir em sua própria solicitação
            if credit_request.employee_id == employee_id:
                return 'Não é possível investir em sua própria solicitação de crédito', 400
            
            # Calcular quanto já foi investido
            invested_amount = sum(inv.amount for inv in credit_request.investments)
            remaining_amount = credit_request.amount - invested_amount
            
            # Validar o valor do investimento
            if amount < InvestmentService.MIN_INVESTMENT_AMOUNT:
                return f'O valor mínimo para investimento é R$ {InvestmentService.MIN_INVESTMENT_AMOUNT:.2f}', 400
            
            if amount > remaining_amount:
                return f'O valor máximo disponível para investimento é R$ {remaining_amount:.2f}', 400
            
            # Criar o investimento
            investment = Investment(
                employee_id=employee_id,
                credit_request_id=credit_request_id,
                amount=amount,
                created_at=datetime.utcnow()
            )
            
            db.session.add(investment)
            db.session.commit()
            
            # Verificar se a solicitação foi totalmente financiada
            new_invested_amount = invested_amount + amount
            if new_invested_amount >= credit_request.amount:
                credit_request.status = CreditRequestStatus.FUNDED
                db.session.commit()
            
            logging.info(f"Novo investimento criado: ID={investment.id}, Valor={amount}, Funcionário={employee_id}, Solicitação={credit_request_id}")
            return investment.to_dict()
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao criar investimento: {str(e)}")
            return f'Erro ao criar investimento: {str(e)}', 500
