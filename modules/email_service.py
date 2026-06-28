"""
Módulo de Serviço de E-mail
Implementa a lógica de envio de e-mails via SMTP
"""

import smtplib
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Tuple
from config.settings import SMTP_SERVER, SMTP_PORT, MESSAGES
from modules.utils import validate_email


class EmailServiceError(Exception):
    """Exceção customizada para erros no serviço de e-mail"""
    pass


class EmailService:
    """
    Serviço de envio de e-mails via SMTP
    """
    
    def __init__(self, sender_email: str, sender_password: str):
        """
        Inicializa o serviço de e-mail
        
        Args:
            sender_email: E-mail do remetente
            sender_password: Senha de app do remetente
        
        Raises:
            EmailServiceError: Se as credenciais forem inválidas
        """
        if not sender_email or not sender_password:
            raise EmailServiceError("E-mail e senha são obrigatórios")
        
        if not validate_email(sender_email):
            raise EmailServiceError("E-mail do remetente inválido")
        
        self.sender_email = sender_email
        self.sender_password = sender_password
    
    def send_email(self, recipient_email: str, subject: str, body: str) -> bool:
        """
        Envia um e-mail
        
        Args:
            recipient_email: E-mail do destinatário
            subject: Assunto do e-mail
            body: Corpo do e-mail
        
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        
        Raises:
            EmailServiceError: Se houver erro no envio
        """
        try:
            # Validar e-mail do destinatário
            if not validate_email(recipient_email):
                raise EmailServiceError("E-mail do destinatário inválido")
            
            # Validar assunto e corpo
            if not subject or not subject.strip():
                raise EmailServiceError("Assunto do e-mail não pode estar vazio")
            
            if not body or not body.strip():
                raise EmailServiceError("Corpo do e-mail não pode estar vazio")
            
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Conectar ao servidor SMTP e enviar
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            raise EmailServiceError(f"Erro de autenticação SMTP: {e}")
        except smtplib.SMTPException as e:
            raise EmailServiceError(f"Erro SMTP: {e}")
        except Exception as e:
            raise EmailServiceError(f"Erro ao enviar e-mail: {e}")
    
    def send_batch_emails(self, recipients: list, subject: str, body_template: str) -> Tuple[int, int]:
        """
        Envia e-mails em lote
        
        Args:
            recipients: Lista de e-mails dos destinatários
            subject: Assunto do e-mail
            body_template: Template do corpo do e-mail (pode conter placeholders)
        
        Returns:
            Tuple[int, int]: (número de e-mails enviados com sucesso, número de falhas)
        """
        sent = 0
        failed = 0
        
        for recipient in recipients:
            try:
                self.send_email(recipient, subject, body_template)
                sent += 1
            except EmailServiceError as e:
                st.warning(f"Falha ao enviar para {recipient}: {e}")
                failed += 1
        
        return sent, failed


def validate_email_credentials(email: str, password: str) -> bool:
    """
    Valida as credenciais de e-mail
    
    Args:
        email: E-mail do remetente
        password: Senha de app do remetente
    
    Returns:
        bool: True se as credenciais são válidas, False caso contrário
    """
    if not email or not password:
        st.error(MESSAGES["error_email_credentials"])
        return False
    
    if not validate_email(email):
        st.error("E-mail inválido")
        return False
    
    return True


def send_email_safely(sender_email: str, sender_password: str, recipient_email: str, 
                      subject: str, body: str) -> bool:
    """
    Função auxiliar para enviar e-mail com tratamento de erros
    
    Args:
        sender_email: E-mail do remetente
        sender_password: Senha de app do remetente
        recipient_email: E-mail do destinatário
        subject: Assunto do e-mail
        body: Corpo do e-mail
    
    Returns:
        bool: True se enviado com sucesso, False caso contrário
    """
    try:
        # Validar credenciais
        if not validate_email_credentials(sender_email, sender_password):
            return False
        
        # Validar destinatário
        if not recipient_email or not recipient_email.strip():
            st.error(MESSAGES["error_email_destination"])
            return False
        
        # Criar serviço e enviar
        service = EmailService(sender_email, sender_password)
        success = service.send_email(recipient_email, subject, body)
        
        if success:
            success_msg = MESSAGES["success_email"].format(email=recipient_email)
            st.success(success_msg)
        
        return success
        
    except EmailServiceError as e:
        error_msg = MESSAGES["error_smtp"].format(error=str(e))
        st.error(error_msg)
        return False
    except Exception as e:
        error_msg = MESSAGES["error_smtp"].format(error=str(e))
        st.error(error_msg)
        return False
