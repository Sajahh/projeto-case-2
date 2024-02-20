import json
from django.test import TestCase, Client
from django.urls import reverse
from auth_class.models import CustomUser


class AuthClassTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser', email='testuser@example.com', password='testpass')

        self.register_url = reverse(
            'auth_action', kwargs={'action': 'register'})

        self.login_url = reverse('auth_action', kwargs={'action': 'login'})

    # SECTION - Registro
    def test_deve_retornar_400_quando_faltar_dados_na_requisicao(self):
        # NOTE - Teste de dados incompletos

        data = {'username': 'newuser', 'password': 'newpass'}
        response = self.client.post(self.register_url, json.dumps(
            data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {
                         'error': 'Dados incompletos.'})

    def test_deve_retornar_400_quando_o_email_da_requisicao_ja_exisitr_no_banco_de_dados(self):
        # NOTE - Teste de email já existente
        data = {'username': 'newuser',
                'email': 'testuser@example.com', 'password': 'newpass'}
        response = self.client.post(self.register_url, json.dumps(
            data), content_type='application/json')

        self.assertEqual(response.status_code, 400)

        self.assertEqual(json.loads(response.content), {
                         'error': 'Este email já está em uso.'})

    # SECTION - Login

    def test_login_success(self):
        # Dados de teste
        data = {'username': 'testuser@example.com', 'password': 'testpass'}

        # Url para o login
        login_url = reverse('auth_action', kwargs={'action': 'login'})

        # Enviando a requisição
        response = self.client.post(login_url, data=json.dumps(
            data), content_type='application/json')
        response_data = response.json()
        

        # Asserts
        self.assertEqual(response.status_code, 200)

        # Verificar se a mensagem de sucesso está presente
        self.assertEqual(response_data.get('message'), 'Logado com sucesso.')

        # Verificar se o token está presente na resposta
        self.assertIn('token', response_data)
        # Garantir que o token não é vazio
        self.assertTrue(response_data['token'])

    def test_login_invalid_email(self):

        data = {'email': 'notregistered@example.com', 'password': 'testpass'}

        login_url = reverse('auth_action', kwargs={'action': 'login'})

        response = self.client.post(login_url, data=json.dumps(
            data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {
                         'error': 'Usuário ou senha inválidos.'})

    def test_login_invalid_password(self):
        # Dados de teste
        data = {'email': 'testuser@example.com', 'password': 'wrongpassword'}

        # Url para o login
        login_url = reverse('auth_action', kwargs={'action': 'login'})

        # Enviando a requisição
        response = self.client.post(login_url, data=json.dumps(
            data), content_type='application/json')

        # Asserts
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {
            'error': 'Usuário ou senha inválidos.'})

    def test_login_missing_data(self):
        # Dados de teste
        data = {'email': 'testuser@example.com'}

        # Url para o login
        login_url = reverse('auth_action', kwargs={'action': 'login'})

        # Enviando a requisição
        response = self.client.post(login_url, data=json.dumps(
            data), content_type='application/json')

        # Asserts
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {
                         'error': 'Usuário ou senha inválidos.'})

    def test_login_returns_token(self):
        data = {'username': 'testuser@example.com', 'password': 'testpass'}
        response = self.client.post(self.login_url, data=json.dumps(
            data), content_type='application/json')
        self.assertIn('token', response.json())
        self.assertEqual(response.status_code, 200)
    #!SECTION

    # SECTION - Logout
    def test_logout_success(self):
        # Url para o logout
        logout_url = reverse('auth_action', kwargs={'action': 'logout'})

        # Enviando a requisição
        response = self.client.post(logout_url)

        # Asserts
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
                         'message': 'Deslogado com sucesso.'})

    #!SECTION
