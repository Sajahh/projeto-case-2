import logging
from math import e
import requests
import json
from .models import Venda
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import os


load_dotenv()
logger = logging.getLogger(__name__)

APP_KEY = os.getenv('APP_KEY')
APP_SECRET = os.getenv('APP_SECRET')


class OmieVendas:
    def __init__(self, app_key, app_secret):
        self.app_key = app_key
        self.app_secret = app_secret
        self.url = 'https://app.omie.com.br/api/v1/produtos/pedido/'

    def get_vendas(self):
        """
        Recupera uma lista de vendas por meio da API 'ListarPedidos' da Omie e salva no banco de dados.

        :return: Uma lista de dicionarios de venda.
        :rtype: list[Venda<models.Venda>]
        :raises: Exception em caso de erro HTTP, resposta inválida da API ou erro geral durante o processo.
        """
        try:
            vendas = []
            pagina = 1
            total_paginas = 1

            while pagina <= total_paginas:
                payload = json.dumps({
                    "call": 'ListarPedidos',
                    "app_key": self.app_key,
                    "app_secret": self.app_secret,
                    "param": [{
                        "pagina": pagina,
                        "registros_por_pagina": 500,
                        "apenas_importado_api": "N"
                    }]
                })

                headers = {'Content-Type': 'application/json'}
                try:
                    response = requests.post(
                        url=self.url, headers=headers, data=payload)
                except Exception as e:
                    logger.critical(
                        f'Erro no response de na busca das vendas: {e}', exc_info=True)
                    raise e

                if response.status_code != 200:
                    raise Exception(
                        f"Erro HTTP ao buscar vendas: {response.status_code}")

                response_data = response.json()

                vendas_da_pagina = response_data.get(
                    "pedido_venda_produto", [])

                for dados_venda in vendas_da_pagina:
                    if dados_venda['infoCadastro']['faturado'] != 'S':
                        vendas.append(dados_venda)

                total_paginas = response_data.get("total_de_paginas", 1)
                pagina += 1

            return vendas
        except Exception as e:
            logger.critical(
                f'Erro no TRY/EXCEPT geral de buscar vendas: {e}', exc_info=True)
            raise e

    def consultar_pedido(self, numero_pedido):
        """
        Consulta um pedido de venda por meio da API de "ConsultarPedido" da Omie.

        :param numero_pedido: O número do pedido de venda a ser consultado.
        :ptype numero_pedido: int ou str
        :return: Um dicionário contendo informações sobre o pedido de venda.
        :rtype: dict
        :raises: Exception em caso de erro HTTP, resposta inválida da API ou se o campo 'pedido_venda_produto' não for encontrado na resposta.
        """

        payload = json.dumps({
            "call": 'ConsultarPedido',
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [{
                    "numero_pedido": numero_pedido,
            }]
        })
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.url, headers=headers, data=payload)
        response_data = response.json()
        if response.status_code != 200:
            raise Exception(
                f"Erro HTTP ao consultar pedido: {response.status_code} / {response_data}")
        response_data = response.json()
        if 'pedido_venda_produto' not in response_data:
            raise KeyError(
                'Campo pedido_venda_produto não encontrado na resposta')
        return response_data['pedido_venda_produto']

    def alterar_pedido(self, pedido):
        """
        Utiliza a API de 'AlterarPedidoVenda" da Omie pra adicionar as tags necessárias e requisitar o adiantamento das parcelas do pedido de venda através da alteração do mesmo.

        :param pedido: Um dicionário contendo detalhes do pedido a ser alterado.
        :type pedido: dict
        :return: Um JSON com a resposta da API.
        :rtype: dict
        :raises: Exception em caso de erro HTTP, resposta inválida da API ou erro geral durante o processo.
        """
        try:
            payload = json.dumps({
                "call": 'AlterarPedidoVenda',
                "app_key": self.app_key,
                "app_secret": self.app_secret,
                "param": [pedido]
            })
            headers = {'Content-Type': 'application/json'}
            response = requests.post(self.url, headers=headers, data=payload)
            if response.status_code != 200:
                raise Exception(
                    f"Erro HTTP ao alterar pedido: {response.status_code} / {response.json()}")
            response_data = response.json()
            if 'descricao_status' not in response_data:
                logger.critical(
                    f'Erro no response da API de alterar pedido: {response_data}', exc_info=True)
                raise KeyError('Pedido nao foi alterado')
            return response_data
        except Exception as e:
            logger.critical(
                f'Erro no TRY/EXCEPT geral de alterar pedido: {e}', exc_info=True)
            raise e

    def set_adiantamentos(self, dados):
        """
        Utiliza o serviço de alterar_pedido para realizar o adiantamento.

        :param dados: Um dicionário contendo informações necessárias para o adiantamento.
                    Deve conter "numerosVendas" (lista com os numeros do pedido do cliente para localizar os pedidos de vendas a adiantar)
                    e "dataVencimento" (data de vencimento inicial no formato "%d/%m/%Y").
        :type dados: dict
        :return: Um dicionário com informações sobre o resultado da operação.
                Em caso de sucesso, retorna {"status_code": 200, "message": "Todos os pedidos foram adiantados com sucesso"}.
                Em caso de erros, retorna uma lista com os pedidos que não foram adiantados e o erro para que seja analisado.
        :rtype: dict
        :pedidos_pra_excluir: list[str] Lista com os números dos pedidos que foram adiantados com sucesso.
        :error_list: dict["numero_pedido_cliente": str, "erro": str] Lista com os pedidos que não foram adiantados e o erro para que seja analisado.
        :raises: Exception em caso de erro crítico durante o processo.
        """
        try:

            vendas_a_adiantar = dados["numerosVendas"]
            data_vencimento_inicial = datetime.strptime(
                dados["dataVencimento"], "%d/%m/%Y")
            pedidos_para_excluir = []
            erros = []

            for numero_pedido_cliente in vendas_a_adiantar:
                try:
                    venda = Venda.objects.get(
                        numero_pedido_cliente=numero_pedido_cliente)
                    parcelas = venda.parcelas

                    for i, parcela in enumerate(parcelas):
                        parcela['parcela_adiantamento'] = "S"
                        parcela['categoria_adiantamento'] = "1.04.01"
                        parcela['conta_corrente_adiantamento'] = "2135259563"
                        nova_data = data_vencimento_inicial + \
                            relativedelta(months=+i)
                        parcela['data_vencimento'] = nova_data.strftime(
                            '%d/%m/%Y')

                    venda.parcelas = parcelas
                    venda.save()

                    detalhes_pedido = {
                        "cabecalho": {"codigo_pedido": venda.codigo_pedido},
                        "lista_parcelas": {"parcela": parcelas}
                    }

                    resposta_adiantamento = self.alterar_pedido(
                        detalhes_pedido)
                    if resposta_adiantamento.get('descricao_status') != 'Pedido alterado com sucesso!':
                        logger.critical(
                            f'Erro ao adiantar pedido: {resposta_adiantamento}', exc_info=True)
                        erros.append(
                            {"numero_pedido_cliente": numero_pedido_cliente, "erro": "Falha ao alterar pedido"})
                    else:
                        print(
                            f'Pedido {numero_pedido_cliente} adiantado com sucesso.')
                        pedidos_para_excluir.append(numero_pedido_cliente)

                except Venda.DoesNotExist:
                    erros.append(
                        {"numero_pedido_cliente": numero_pedido_cliente, "erro": "Pedido não encontrado"})
                except Exception as e:
                    erros.append(
                        {"numero_pedido_cliente": numero_pedido_cliente, "erro": str(e)})

            if pedidos_para_excluir:
                self.excluir_pedidos(pedidos_para_excluir)

            if erros:
                logger.error(
                    f'Erros ao adiantar pedidos: {erros}', exc_info=True)
                return {"status_code": 500, "message": "Erros encontrados", "erros": erros}
            else:
                return {"status_code": 200, "message": "Todos os pedidos foram adiantados com sucesso"}
        except Exception as e:
            logger.critical(
                f'Erro ao adiantar pedidos: {e}', exc_info=True)
            raise e

    def excluir_pedidos(self, pedidos):
        """
        Exclui vendas do banco de dados com base em uma lista de números de pedido.

        :param pedidos: Uma lista de números de pedidos.
        """
        try:

            for numero_pedido_cliente in pedidos:
                Venda.objects.filter(
                    numero_pedido_cliente=numero_pedido_cliente).delete()
        except Exception as e:
            logger.error(
                f'Erro ao excluir pedidos: {e}', exc_info=True)
            raise e
