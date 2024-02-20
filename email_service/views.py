from email import message
import smtplib
import logging

logger = logging.getLogger(__name__)


class EmailSender:
    @staticmethod
    def send_email(email_destino: str, assunto: str, body: str, email_remetente: str, senha: str):
        """
        //NOTE - Enviar Email
        Envia um email para o destinatário

        Args:
            email_destino (str): email de destino
            assunto (str): assunto do email
            body (str): conteúdo do email
        """
        try:
            corpo_email = body

            msg = message.Message()
            msg['Subject'] = assunto
            msg['From'] = email_remetente
            msg['To'] = email_destino
            password = senha
            msg.add_header('Content-Type', 'text/html')
            msg.set_payload(corpo_email)

            s = smtplib.SMTP('smtp.gmail.com: 587')
            s.starttls()

            s.login(msg['From'], password)
            s.sendmail(msg['From'], [msg['To']],
                       msg.as_string().encode('utf-8'))
            print('Email enviado')
        except Exception as e:
            logger.error(f'Erro ao enviar email: {e}', exc_info=True)
            print(f'Erro ao enviar email: {e}')
