import pytest
import requests_mock
from django.test import TestCase
from django.urls import reverse


@pytest.mark.django_db
class OmieVendasRouteTests(TestCase):

    @requests_mock.Mocker()
    def test_get_vendas_success(self, mock):
        mock.post('https://app.omie.com.br/api/v1/produtos/pedido/',
                  json={"mensagem": 'Sucesso!'})
        response = self.client.get(reverse('get_vendas'))
        print(f'Response: {response}')

        self.assertEqual(response.status_code, 200)

    @requests_mock.Mocker()
    def test_get_vendas_failure(self, mock):
        mock.post('https://app.omie.com.br/api/v1/produtos/pedido/',
                  status_code=500, json={"error": "Server Error"})
        response = self.client.get(reverse('get_vendas'))
        self.assertEqual(response.status_code, 500)

    @requests_mock.Mocker()
    def test_consultar_pedido_success(self, mock):
        mock.post('https://app.omie.com.br/api/v1/produtos/pedido/',
                  json={"pedido_venda_produto": "detalhes"})
        # Alteração aqui: Usando json= para enviar dados JSON
        response = self.client.post(
            reverse('consultar_pedido'), json={'codigo_pedido': 6706980855}, content_type='application/json')
        self.assertEqual(response.status_code, 200)

    @requests_mock.Mocker()
    def test_consultar_pedido_failure(self, mock):
        mock.post('https://app.omie.com.br/api/v1/produtos/pedido/',
                  status_code=500, json={"error": "Server Error"})
        # Alteração aqui também
        response = self.client.post(
            reverse('consultar_pedido'), json={'codigo_pedido': 6706980855}, content_type='application/json')
        self.assertEqual(response.status_code, 500)

    @requests_mock.Mocker()
    def test_alterar_pedido_success(self, mock):
        mock.post('https://app.omie.com.br/api/v1/produtos/pedido/',
                  json={'descricao_status': 'Pedido alterado com sucesso'})
        # Alteração: Usando json=
        response = self.client.post(
            reverse('alterar_pedido'), json={"pedido": "infos_pedido + tag de adiantamento"}, content_type='application/json')

        self.assertEqual(response.status_code, 200)

    @requests_mock.Mocker()
    def test_alterar_pedido_failure(self, mock):
        mock.post('https://app.omie.com.br/api/v1/produtos/pedido/',
                  status_code=500, json={"error": "Server Error"})
        # Alteração aqui
        response = self.client.post(
            reverse('alterar_pedido'), json={'pedido': {}}, content_type='application/json')
        self.assertEqual(response.status_code, 500)

    @requests_mock.Mocker()
    def test_set_adiantamentos_success(self, mock):

        mock.post('https://app.omie.com.br/api/v1/produtos/pedido/',
                  json={"descricao_status": "Pedido alterado com sucesso"}, status_code=201)

        # REVIEW - Confirmar com o front se o formato do JSON está condizente com o esperado
        data_list = {"vendas_a_adiantar": [{"numero_pedido": "81"}]}

        response = self.client.post(
            reverse('set_adiantamentos'), data=data_list, content_type='application/json')

        self.assertEqual(response.status_code, 201)

    @requests_mock.Mocker()
    def test_set_adiantamentos_failure(self, mock):

        mock.post('https://app.omie.com.br/api/v1/produtos/pedido/',
                  status_code=500, json={"error": "Server Error"})
        # Alteração aqui também
        response = self.client.post(reverse('set_adiantamentos'), json={"infos_pedido": "+ tag de adiantamento",
                                                                        "numero_pedido": "81"}, content_type='application/json')
        self.assertEqual(response.status_code, 500)
