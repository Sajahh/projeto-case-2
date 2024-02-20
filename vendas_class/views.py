from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods

from vendas_class.tests.test_omie_vendas import omie_vendas
from .services import OmieVendas
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Venda
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)

APP_KEY = os.getenv('APP_KEY')
APP_SECRET = os.getenv('APP_SECRET')


@csrf_exempt
@require_http_methods(["GET"])
def get_vendas_view(request):
    try:
        # Primeiro, tente buscar vendas no banco de dados
        vendas = Venda.objects.all()
        if not vendas.exists():
            # Se não houver vendas, chame a API da Omie
            omie_vendas = OmieVendas(APP_KEY, APP_SECRET)
            vendas_nao_faturadas = omie_vendas.get_vendas()
            print(vendas_nao_faturadas)

            for dados_venda in vendas_nao_faturadas:

                try:

                    venda = Venda.criar_de_api(dados_venda)
                    venda.save()
                except Exception as e:

                    logger.error(
                        f"Erro ao salvar venda do pedido {e}", exc_info=True)
                    continue

            # Atualize a lista de vendas após salvá-las no banco de dados
            vendas = Venda.objects.all()

        # Preparar os dados para resposta
        vendas_data = [{
            'numero_pedido': venda.numero_pedido,
            'numero_pedido_cliente': venda.numero_pedido_cliente,
            'data_vencimento': venda.data_vencimento.strftime('%d/%m/%Y') if venda.data_vencimento else None,
            'data_emissao': venda.data_emissao.strftime('%d/%m/%Y'),
            'valor_total_pedido': venda.valor_total_pedido,
            'produtos': venda.produtos
        } for venda in vendas]

        return JsonResponse(vendas_data, safe=False, status=200)

    except Exception as e:
        logger.critical(f'Erro na rota de buscar vendas: {e}', exc_info=True)
        return HttpResponse(str(e), status=500)


@csrf_exempt
@require_http_methods(["POST"])
def alterar_pedido_view(request):
    try:
        pedido = json.loads(request.body)
        omie_vendas = OmieVendas(APP_KEY, APP_SECRET)
        try:
            resposta = omie_vendas.alterar_pedido(pedido)
            return JsonResponse(resposta, status=200)

        except Exception as e:
            logger.error(
                f'Erro na resposta do serviço de alterar pedidos: {e}', exc_info=True)
            return HttpResponse(str(e), status=500)
    except Exception as e:
        logger.critical(f'Erro na rota de alterar pedidos: {e}', exc_info=True)
        return HttpResponse(str(e), status=500)


@csrf_exempt
@require_http_methods(["POST"])
def set_adiantamentos_view(request):
    try:
        vendas_a_adiantar = json.loads(request.body)

        omie_vendas = OmieVendas(APP_KEY, APP_SECRET)
        resultado = omie_vendas.set_adiantamentos(vendas_a_adiantar)

        if resultado['status_code'] == 200:
            return JsonResponse({'message': resultado['message']}, status=200)
        elif resultado['status_code'] == 404:
            return JsonResponse({'message': resultado['message']}, status=404)
        else:
            if 'erros' in resultado:
                return JsonResponse({'message': resultado['message'], 'erros': resultado['erros']}, status=resultado['status_code'])
            else:
                return JsonResponse({'message': resultado['message']}, status=resultado['status_code'])

    except Exception as e:
        logger.critical(
            f'Erro na rota de adiantar pedidos: {e}', exc_info=True)
        return HttpResponse(str(e), status=500)


def webhook_omie(request):
    try:
        data = json.loads(request.body)
        numero_pedido = data.get('numero_pedido')

        if numero_pedido is None:
            raise ValueError("Número do pedido não fornecido")

        omie_vendas = OmieVendas(APP_KEY, APP_SECRET)
        dados_pedido = omie_vendas.consultar_pedido(numero_pedido)

        venda = Venda.criar_de_api(dados_pedido)
        venda.save()

        return JsonResponse({"message": "Pedido salvo com sucesso"}, status=200)
    except Exception as e:
        logger.critical(
            f'Erro no webhook de vendas: {e}', exc_info=True)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
