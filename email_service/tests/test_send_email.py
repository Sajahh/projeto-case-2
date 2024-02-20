import pytest
from unittest.mock import patch, MagicMock
from email_service.views import EmailSender


class TestEmailSender:
    @patch('email_service.views.smtplib.SMTP')
    def test_enviar_email_success(self, mock_smtp):
        # Simular o servidor SMTP e o processo de envio de e-mail
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        # Chamar enviar_email com dados de teste
        EmailSender.send_email('test@example.com', 'Assunto de Teste',
                               'Corpo de Teste', 'sender@example.com', 'senha')

        # Verificar se o servidor SMTP foi chamado corretamente
        mock_smtp.assert_called_with('smtp.gmail.com: 587')
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_with('sender@example.com', 'senha')
        mock_server.sendmail.assert_called()

        # Adicionar mais asserções para verificar o conteúdo do e-mail enviado

    # Adicionar mais casos de teste para tratar erros ou parâmetros incorretos
