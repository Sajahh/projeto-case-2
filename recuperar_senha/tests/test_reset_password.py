from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from recuperar_senha.models import PasswordResetToken
from django.contrib.auth import get_user_model
import json
import random

User = get_user_model()


class PasswordResetTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='testpass')
        self.reset_password_request_url = reverse(
            'reset_action', kwargs={'action': 'request_reset'})
        self.reset_password_url = reverse(
            'reset_action', kwargs={'action': 'reset'})

    @patch('recuperar_senha.views.EmailSender.send_email')
    def test_request_password_reset_with_valid_email(self, mock_send_email):
        data = json.dumps({'email': self.user.email})
        response = self.client.post(
            self.reset_password_request_url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(PasswordResetToken.objects.filter(
            user=self.user).exists())
        mock_send_email.assert_called_once()

    def test_request_password_reset_with_invalid_email(self):
        data = json.dumps({'email': 'invalid@example.com'})
        response = self.client.post(
            self.reset_password_request_url, data, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_reset_password_with_valid_verification_code(self):
        # Gera um código de verificação de 6 dígitos
        verification_code = random.randint(100000, 999999)
        # Cria um token com o código de verificação
        token = PasswordResetToken.objects.create(
            user=self.user, token=verification_code)

        new_password = 'newpassword123'
        data = {
            'verification_code': verification_code,  # Utiliza o código de verificação
            'new_password': new_password
        }
        response = self.client.post(self.reset_password_url, data=json.dumps(
            data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))

    def test_reset_password_with_invalid_token(self):
        data = {
            'token': '7770fa00-854d-11ee-b9d1-0242ac120002',
            'new_password': 'newpassword123'
        }
        response = self.client.post(self.reset_password_url, data=json.dumps(
            data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
