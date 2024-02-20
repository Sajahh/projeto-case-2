import logging
from email_service.views import EmailSender  # Importe sua classe EmailSender
from dotenv import load_dotenv
import os

load_dotenv()


class EmailErrorHandler(logging.Handler):
    def __init__(self, email_destino, assunto, email_remetente, senha, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.email_destino = email_destino
        self.assunto = assunto
        self.email_remetente = email_remetente
        self.senha = senha

    def emit(self, record):
        log_entry = self.format(record)
        body = f"Ocorreu um erro:\n\n{log_entry}"

        try:
            EmailSender.send_email(
                email_destino=self.email_destino,
                assunto=self.assunto,
                body=body,
                email_remetente=self.email_remetente,
                senha=self.senha
            )
        except Exception as e:
            print(f"Erro ao enviar email de log: {e}")


# Configuração do logging para usar o EmailErrorHandler
logger = logging.getLogger(__name__)
email_handler = EmailErrorHandler(
    email_destino="email_destino@email.com",
    assunto="Erro no Sistema",
    email_remetente="email_remetente@email.com",
    senha=os.getenv("SECRETKEY_EMAIL"),
)
logger.addHandler(email_handler)
email_handler.setLevel(logging.CRITICAL)
