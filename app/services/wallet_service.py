from app import db
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction, TransactionType
from app.models.payment import Payment, PaymentType, PaymentStatus
from app.models.investment import Investment
from datetime import datetime, timedelta
import logging

class WalletService:
    @staticmethod
    def get_wallet_by_employee(employee_id):
        """Retorna a carteira de um funcionário"""
        try:
            wallet = Wallet.query.filter_by(employee_id=employee_id).first()
            if not wallet:
                # Cria uma nova carteira se não existir
                wallet = Wallet(employee_id=employee_id)
                db.session.add(wallet)
                db.session.commit()
            return wallet
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao buscar carteira: {str(e)}")
            raise
    
    @staticmethod
    def deposit(employee_id, amount):
        """Realiza um depósito na carteira do funcionário"""
        try:
            wallet = WalletService.get_wallet_by_employee(employee_id)
            
            # Adiciona o saldo
            wallet.add_balance(amount)
            
            # Registra a transação
            transaction = WalletTransaction(
                wallet_id=wallet.id,
                type=TransactionType.DEPOSIT,
                amount=amount,
                description=f"Depósito de R$ {amount:.2f}"
            )
            db.session.add(transaction)
            db.session.commit()
            
            return wallet, transaction
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao realizar depósito: {str(e)}")
            raise
    
    @staticmethod
    def withdraw(employee_id, amount):
        """Realiza um saque da carteira do funcionário"""
        try:
            wallet = WalletService.get_wallet_by_employee(employee_id)
            
            # Subtrai o saldo
            wallet.subtract_balance(amount)
            
            # Registra a transação
            transaction = WalletTransaction(
                wallet_id=wallet.id,
                type=TransactionType.WITHDRAWAL,
                amount=amount,
                description=f"Saque de R$ {amount:.2f}"
            )
            db.session.add(transaction)
            db.session.commit()
            
            return wallet, transaction
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao realizar saque: {str(e)}")
            raise
    
    @staticmethod
    def invest(employee_id, investment_id, amount):
        """Realiza um investimento usando o saldo da carteira"""
        try:
            wallet = WalletService.get_wallet_by_employee(employee_id)
            investment = Investment.query.get(investment_id)
            
            if not investment:
                raise ValueError("Investimento não encontrado")
            
            # Subtrai o saldo
            wallet.subtract_balance(amount)
            
            # Registra a transação
            transaction = WalletTransaction(
                wallet_id=wallet.id,
                type=TransactionType.INVESTMENT,
                amount=amount,
                description=f"Investimento em solicitação #{investment.credit_request_id}",
                investment_id=investment_id
            )
            db.session.add(transaction)
            db.session.commit()
            
            return wallet, transaction
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao realizar investimento: {str(e)}")
            raise
    
    @staticmethod
    def get_transactions(employee_id, transaction_type=None):
        """Retorna as transações da carteira do funcionário"""
        try:
            wallet = WalletService.get_wallet_by_employee(employee_id)
            query = WalletTransaction.query.filter_by(wallet_id=wallet.id)
            
            if transaction_type:
                query = query.filter_by(type=transaction_type)
            
            return query.order_by(WalletTransaction.created_at.desc()).all()
        except Exception as e:
            logging.error(f"Erro ao buscar transações: {str(e)}")
            raise
    
    @staticmethod
    def get_payments(employee_id, status=None):
        """Retorna os pagamentos de dividendos/juros do funcionário"""
        try:
            wallet = WalletService.get_wallet_by_employee(employee_id)
            investments = Investment.query.filter_by(employee_id=employee_id).all()
            investment_ids = [inv.id for inv in investments]
            
            query = Payment.query.filter(Payment.investment_id.in_(investment_ids))
            
            if status:
                query = query.filter_by(status=status)
            
            return query.order_by(Payment.due_date.desc()).all()
        except Exception as e:
            logging.error(f"Erro ao buscar pagamentos: {str(e)}")
            raise
    
    @staticmethod
    def process_payment(payment_id):
        """Processa um pagamento de dividendo/juros"""
        try:
            payment = Payment.query.get(payment_id)
            if not payment:
                raise ValueError("Pagamento não encontrado")
            
            if payment.status != PaymentStatus.PENDING:
                raise ValueError("Pagamento já processado")
            
            # Obtém a carteira do funcionário
            wallet = WalletService.get_wallet_by_employee(payment.investment.employee_id)
            
            # Adiciona o valor à carteira
            wallet.add_balance(payment.amount)
            
            # Registra a transação
            transaction = WalletTransaction(
                wallet_id=wallet.id,
                type=TransactionType.DIVIDEND if payment.type == PaymentType.DIVIDEND else TransactionType.INTEREST,
                amount=payment.amount,
                description=f"Recebimento de {payment.type} do investimento #{payment.investment_id}",
                investment_id=payment.investment_id
            )
            db.session.add(transaction)
            
            # Marca o pagamento como realizado
            payment.mark_as_paid()
            
            db.session.commit()
            return payment, transaction
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao processar pagamento: {str(e)}")
            raise
    
    @staticmethod
    def schedule_payments(investment_id):
        """Agenda os pagamentos de dividendos/juros para um investimento"""
        try:
            investment = Investment.query.get(investment_id)
            if not investment:
                raise ValueError("Investimento não encontrado")
            
            credit_request = investment.credit_request
            term_months = credit_request.term_months
            monthly_interest = credit_request.interest_rate / 100  # Converte para decimal
            
            # Calcula o valor mensal de juros
            monthly_interest_amount = investment.amount * monthly_interest
            
            # Agenda os pagamentos mensais
            for month in range(1, term_months + 1):
                due_date = datetime.utcnow() + timedelta(days=30 * month)
                
                # Cria o pagamento de juros
                interest_payment = Payment(
                    investment_id=investment_id,
                    type=PaymentType.INTEREST,
                    amount=monthly_interest_amount,
                    due_date=due_date
                )
                db.session.add(interest_payment)
                
                # No último mês, adiciona o pagamento do dividendo (retorno do principal)
                if month == term_months:
                    dividend_payment = Payment(
                        investment_id=investment_id,
                        type=PaymentType.DIVIDEND,
                        amount=investment.amount,
                        due_date=due_date
                    )
                    db.session.add(dividend_payment)
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao agendar pagamentos: {str(e)}")
            raise 