import pytest
import requests
import requests_mock
from vendas_class.services import OmieVendas
from vendas_class.models import Venda
from datetime import datetime


@pytest.fixture
def omie_vendas():
    return OmieVendas(app_key="test_key", app_secret="test_secret")


@pytest.mark.django_db
def test_constructor(omie_vendas):
    assert omie_vendas.app_key == "test_key"
    assert omie_vendas.app_secret == "test_secret"
    assert omie_vendas.url == "https://app.omie.com.br/api/v1/produtos/pedido/"


@pytest.mark.django_db
def test_get_vendas_success(omie_vendas):
    mock_response = {
        "pedido_venda_produto": [
            {
                "cabecalho": {"numero_pedido": "5", "codigo_pedido": 2095664576, "etapa": "60"},
                "infoCadastro": {"dInc": "11/07/2023"},
                "total_pedido": {"valor_total_pedido": 150},
                "det": [
                    {
                        "produto": {"codigo": "1000", "descricao": "Mouse sem fio Microsoft", "valor_unitario": 150}
                    }
                ],
                "lista_parcelas": {"parcela": [{"data_vencimento": "11/07/2023", "numero_parcela": 1, "valor": 150}]}
            }
        ],
        "total_de_paginas": 1
    }

    with requests_mock.Mocker() as m:
        m.post("https://app.omie.com.br/api/v1/produtos/pedido/",
               json=mock_response)
        omie_vendas.get_vendas()

        vendas = Venda.objects.all()
        assert vendas.count() == 1
        venda = vendas.first()
        assert venda.numero_pedido == 5
        assert venda.codigo_pedido == 2095664576
        assert venda.data_emissao == datetime.strptime(
            "11/07/2023", '%d/%m/%Y').date()
        assert venda.valor_total_pedido == 150
        assert len(venda.produtos) == 1
        assert venda.produtos[0]["codigo"] == "1000"
        assert venda.produtos[0]["descricao"] == "Mouse sem fio Microsoft"
        assert venda.produtos[0]["valor"] == 150
        assert len(venda.parcelas) == 1
        assert venda.parcelas[0]["numero_parcela"] == 1
        assert venda.parcelas


@pytest.mark.django_db
def test_get_vendas_exception(omie_vendas):
    with requests_mock.Mocker() as m:
        m.post("https://app.omie.com.br/api/v1/produtos/pedido/",
               exc=requests.exceptions.ConnectTimeout)
        with pytest.raises(Exception) as excinfo:
            omie_vendas.get_vendas()
        assert "Erro ao buscar vendas:" in str(excinfo.value)


@pytest.mark.django_db
def test_pagination(omie_vendas):
    with requests_mock.Mocker() as m:
        m.post("https://app.omie.com.br/api/v1/produtos/pedido/",
               [{"json": {"pedido_venda_produto": [
                   {"cabecalho": {"numero_pedido": 1, "codigo_pedido": 2095664576, "etapa": "60"},
                    "infoCadastro": {"dInc": "11/07/2023"},
                    "total_pedido": {"valor_total_pedido": 150},
                    "det": [
                        {
                            "produto": {"codigo": "1000", "descricao": "Mouse sem fio Microsoft", "valor_unitario": 150}
                        }
                   ],
                       "lista_parcelas": {
                        "parcela": [{"data_vencimento": "11/07/2023", "numero_parcela": 1, "percentual": 100, "quantidade_dias": 0, "valor": 150}]
                   }
                   }],
                   "total_de_paginas": 2}, "status_code": 200},
                {"json": {"pedido_venda_produto": [
                    {"cabecalho": {"numero_pedido": 2, "codigo_pedido": 2095664577, "etapa": "60"},
                     "infoCadastro": {"dInc": "12/07/2023"},
                     "total_pedido": {"valor_total_pedido": 200},
                     "det": [
                        {
                            "produto": {"codigo": "1001", "descricao": "Teclado sem fio Logitech", "valor_unitario": 200}
                        }
                    ],
                        "lista_parcelas": {
                        "parcela": [{"data_vencimento": "12/07/2023", "numero_parcela": 1, "percentual": 100, "quantidade_dias": 0, "valor": 200}]
                    }
                    }],
                    "total_de_paginas": 2}, "status_code": 200}])

        omie_vendas.get_vendas()

        vendas = Venda.objects.all()
        assert vendas.count() == 2
        venda1, venda2 = vendas[0], vendas[1]
        assert venda1.numero_pedido == 1
        assert venda2.numero_pedido == 2


def test_consultar_pedido_success(omie_vendas):
    with requests_mock.Mocker() as m:
        m.post(omie_vendas.url, json={"pedido_venda_produto": {
               "cabecalho": {"codigo_pedido": 6706980855}}})
        resposta = omie_vendas.consultar_pedido(6706980855)
        assert resposta['pedido_venda_produto']['cabecalho']['codigo_pedido'] == 6706980855


def test_consultar_pedido_http_error(omie_vendas):
    with requests_mock.Mocker() as m:
        m.post(omie_vendas.url, status_code=500)
        with pytest.raises(Exception):

            omie_vendas.consultar_pedido(1)


def test_consultar_pedido_invalid_response(omie_vendas):
    with requests_mock.Mocker() as m:
        m.post(omie_vendas.url, json={"invalid": "response"})
        with pytest.raises(KeyError):
            omie_vendas.consultar_pedido(6706980855)

# REVIEW - Revisar testes de alterar pedido/set_adiantamento, verificar o que é "codigo_Status", ver como vem a respota da API e parametrizar de acordo com isso e/ou com a certificação do adiantamento


def test_alterar_pedido_success(omie_vendas):
    with requests_mock.Mocker() as m:
        m.post(omie_vendas.url, json={
               "descricao_status": "Pedido alterado com sucesso"})
        resposta = omie_vendas.alterar_pedido(
            {"pedido": "infos_pedido + tag de adiantamento"})
        assert resposta["descricao_status"] == "Pedido alterado com sucesso"


def test_alterar_pedido_invalid_response(omie_vendas):
    with requests_mock.Mocker() as m:
        res = m.post(omie_vendas.url, json={"invalid": "response"})

        with pytest.raises(KeyError):
            omie_vendas.alterar_pedido({"algum_dado": "valor"})


def test_alterar_pedido_http_error(omie_vendas):
    with requests_mock.Mocker() as m:
        m.post(omie_vendas.url, status_code=500)
        with pytest.raises(Exception):
            omie_vendas.alterar_pedido({"algum_dado": "valor"})


def test_set_adiantamentos_success(omie_vendas):

    with requests_mock.Mocker() as m:
        m.post(omie_vendas.url, [{"json": {"pedido_venda_produto": {"lista_parcelas": {"parcela": [{}]}}}},
                                 {"json": {"descricao_status": "Pedido alterado com sucesso"}}])
        status = omie_vendas.set_adiantamentos(
            [{"pedido_venda_produto": {

                "lista_parcelas": {"parcela": [{}]}}, "numero_pedido": "81"}])

        assert status == 201


def test_set_adiantamentos_consulta_falha(omie_vendas):

    with requests_mock.Mocker() as m:
        m.post(omie_vendas.url, [{"status_code": 500}])
        status = omie_vendas.set_adiantamentos(
            [{"infos_pedido": "+ tag de adiantamento",
              "numero_pedido": "81"}])
        assert status == 500


def test_set_adiantamentos_alteracao_falha(omie_vendas):

    with requests_mock.Mocker() as m:
        m.post(omie_vendas.url, [{"json": {"pedido_venda_produto": {"lista_parcelas": {"parcela": [{}]}}}},
                                 {"status_code": 500}])
        status = omie_vendas.set_adiantamentos(
            [{"infos_pedido": "+ tag de adiantamento",
              "numero_pedido": "81"}])
        assert status == 500
