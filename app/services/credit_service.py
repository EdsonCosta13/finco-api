from app import db
from app.models.credit_request import CreditRequest, CreditRequestStatus
from app.models.employee import Employee
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import logging

class CreditService:
    # Constantes para validação
    MIN_AMOUNT = 100.0
    MAX_AMOUNT = 10000.0
    MIN_TERM_MONTHS = 3
    MAX_TERM_MONTHS = 36
    MIN_INTEREST_RATE = 0.5
    MAX_INTEREST_RATE = 5.0

    @staticmethod
    def get_all_credit_requests():
        """Retorna todas as solicitações de crédito"""
        try:
            requests = CreditRequest.query.all()
            logging.info(f"Buscando todas as solicitações de crédito. Total encontrado: {len(requests)}")
            return requests
        except Exception as e:
            logging.error(f"Erro ao buscar solicitações: {str(e)}")
            raise
    
    @staticmethod
    def get_credit_requests_by_employee(employee_id):
        """Retorna todas as solicitações de crédito de um funcionário"""
        try:
            requests = CreditRequest.query.filter_by(employee_id=employee_id).all()
            logging.info(f"Buscando solicitações do funcionário {employee_id}. Total encontrado: {len(requests)}")
            return requests
        except Exception as e:
            logging.error(f"Erro ao buscar solicitações do funcionário: {str(e)}")
            raise
    
    @staticmethod
    def get_credit_request_by_id(credit_id):
        """Retorna uma solicitação de crédito específica"""
        try:
            request = CreditRequest.query.get(credit_id)
            logging.info(f"Buscando solicitação {credit_id}. Encontrada: {request is not None}")
            return request
        except Exception as e:
            logging.error(f"Erro ao buscar solicitação: {str(e)}")
            raise
    
    @staticmethod
    def get_credit_requests_by_company_and_status(company_id, status=None):
        """Retorna todas as solicitações de crédito de uma empresa, opcionalmente filtradas por status"""
        try:
            # Sempre filtra pela empresa do manager
            query = CreditRequest.query.join(Employee).filter(Employee.company_id == company_id)
            
            if status:
                query = query.filter(CreditRequest.status == status)
            
            # Ordena por data de criação, mais recentes primeiro
            query = query.order_by(CreditRequest.created_at.desc())
            
            requests = query.all()
            logging.info(f"Buscando solicitações da empresa {company_id} com status {status}. Total encontrado: {len(requests)}")
            return requests
        except Exception as e:
            logging.error(f"Erro ao buscar solicitações da empresa: {str(e)}")
            raise

    @staticmethod
    def get_pending_credit_requests_by_company(company_id):
        """Retorna todas as solicitações de crédito pendentes de uma empresa"""
        try:
            requests = CreditRequest.query.join(Employee).filter(
                Employee.company_id == company_id,
                CreditRequest.status == CreditRequestStatus.PENDING
            ).order_by(CreditRequest.created_at.desc()).all()
            
            logging.info(f"Buscando solicitações pendentes da empresa {company_id}. Total encontrado: {len(requests)}")
            return requests
        except Exception as e:
            logging.error(f"Erro ao buscar solicitações pendentes da empresa: {str(e)}")
            raise

    @staticmethod
    def create_employee_credit_request(employee_id, amount, term_months, purpose):
        try:
            # Verificar se o funcionário existe
            employee = Employee.query.get(employee_id)
            if not employee:
                return 'Funcionário não encontrado', 404

            # Verificar se já existe uma solicitação pendente
            pending_request = CreditRequest.query.filter_by(
                employee_id=employee_id,
                status=CreditRequestStatus.PENDING
            ).first()
            
            if pending_request:
                return 'Já existe uma solicitação de crédito pendente', 400

            # Validar valores mínimos e máximos
            if amount < 1000:
                return 'O valor mínimo para solicitação é de R$ 1.000,00', 400
            if amount > 50000:
                return 'O valor máximo para solicitação é de R$ 50.000,00', 400
            if term_months < 3:
                return 'O prazo mínimo é de 3 meses', 400
            if term_months > 60:
                return 'O prazo máximo é de 60 meses', 400

            # Calcular taxa de juros base
            base_rate = 0.015  # 1.5% ao mês
            if amount > 25000:
                base_rate -= 0.002  # Redução de 0.2% para valores acima de R$ 25.000
            if term_months > 24:
                base_rate += 0.001  # Aumento de 0.1% para prazos acima de 24 meses

            # Criar solicitação de crédito
            credit_request = CreditRequest(
                employee_id=employee_id,
                amount=amount,
                term_months=term_months,
                purpose=purpose,
                interest_rate=base_rate,
                status=CreditRequestStatus.PENDING
            )

            db.session.add(credit_request)
            db.session.commit()

            return credit_request.to_dict()

        except Exception as e:
            db.session.rollback()
            return f'Erro ao criar solicitação de crédito: {str(e)}', 500
    
    @staticmethod
    def calculate_interest_rate(amount, term_months):
        """Calcula a taxa de juros baseada no valor e prazo"""
        base_rate = CreditService.MIN_INTEREST_RATE
        
        # Ajuste baseado no valor
        if amount > CreditService.MAX_AMOUNT * 0.7:
            base_rate += 0.5
        elif amount > CreditService.MAX_AMOUNT * 0.4:
            base_rate += 0.3
        
        # Ajuste baseado no prazo
        if term_months > CreditService.MAX_TERM_MONTHS * 0.7:
            base_rate += 0.5
        elif term_months > CreditService.MAX_TERM_MONTHS * 0.4:
            base_rate += 0.3
        
        return min(base_rate, CreditService.MAX_INTEREST_RATE)
    
    @staticmethod
    def create_credit_request(data):
        # Check if employee exists
        employee = Employee.query.get(data.get('employee_id'))
        if not employee:
            return None, "Employee not found"
        
        # Check if employee has pending credit requests
        pending_requests = CreditRequest.query.filter_by(
            employee_id=data.get('employee_id'),
            status=CreditRequestStatus.PENDING
        ).first()
        
        if pending_requests:
            return None, "Employee already has a pending credit request"
        
        try:
            credit_request = CreditRequest(
                amount=data.get('amount'),
                interest_rate=data.get('interest_rate'),
                term_months=data.get('term_months'),
                purpose=data.get('purpose'),
                status=CreditRequestStatus.PENDING,
                employee_id=data.get('employee_id')
            )
            
            db.session.add(credit_request)
            db.session.commit()
            return credit_request, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def update_credit_request_status(credit_id, status, company_id):
        """Atualiza o status de uma solicitação de crédito"""
        try:
            credit_request = CreditRequest.query.get(credit_id)
            if not credit_request:
                return None, "Solicitação de crédito não encontrada"
            
            # Verifica se a solicitação pertence à empresa do manager
            employee = Employee.query.get(credit_request.employee_id)
            if not employee or employee.company_id != company_id:
                return None, "Você não tem permissão para gerenciar esta solicitação de crédito"
            
            # Validate status transition
            if credit_request.status == CreditRequestStatus.COMPLETED:
                return None, "Não é possível alterar o status de uma solicitação de crédito concluída"
            
            if credit_request.status == CreditRequestStatus.REJECTED and status != CreditRequestStatus.CANCELLED:
                return None, "Solicitações rejeitadas só podem ser canceladas"
            
            # Apply status update
            credit_request.status = status
            db.session.commit()
            
            logging.info(f"Status da solicitação {credit_id} atualizado para {status}")
            return credit_request, None
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao atualizar status da solicitação {credit_id}: {str(e)}")
            return None, f"Erro ao atualizar status: {str(e)}"
    
    @staticmethod
    def get_funded_amount(credit_id):
        credit_request = CreditRequest.query.get(credit_id)
        if not credit_request:
            return 0
        
        return sum(investment.amount for investment in credit_request.investments)
    
    @staticmethod
    def check_fully_funded(credit_request):
        funded_amount = CreditService.get_funded_amount(credit_request.id)
        if funded_amount >= credit_request.amount:
            credit_request.status = CreditRequestStatus.FUNDED
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_available_credit_requests():
        """Retorna todas as solicitações de crédito aprovadas disponíveis para investimento"""
        try:
            # Busca solicitações aprovadas que ainda não foram totalmente financiadas
            requests = CreditRequest.query.filter(
                CreditRequest.status == CreditRequestStatus.APPROVED
            ).order_by(CreditRequest.created_at.desc()).all()
            
            result = []
            for request in requests:
                # Calcula quanto já foi investido
                invested_amount = sum(investment.amount for investment in request.investments)
                remaining_amount = request.amount - invested_amount
                
                # Só inclui se ainda houver valor disponível para investimento
                if remaining_amount > 0:
                    result.append({
                        'id': request.id,
                        'amount': request.amount,
                        'remaining_amount': remaining_amount,
                        'interest_rate': request.interest_rate,
                        'term_months': request.term_months,
                        'purpose': request.purpose,
                        'employee_name': request.employee.name,
                        'company_name': request.employee.company.name,
                        'created_at': request.created_at.isoformat(),
                        'invested_amount': invested_amount,
                        'investment_percentage': (invested_amount / request.amount) * 100
                    })
            
            logging.info(f"Buscando solicitações disponíveis para investimento. Total encontrado: {len(result)}")
            return result
            
        except Exception as e:
            logging.error(f"Erro ao buscar solicitações disponíveis: {str(e)}")
            raise
