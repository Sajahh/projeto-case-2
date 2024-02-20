from django.db import models
from datetime import datetime


class Venda(models.Model):
    numero_pedido = models.IntegerField(unique=True)
    # FIXME - Definir um default pra numero_pedido_cliente
    numero_pedido_cliente = models.CharField(max_length=20, default='')
    # FIXME - Definir um default pra data_vencimento
    data_vencimento = models.DateField(null=True)
    codigo_pedido = models.IntegerField(unique=True)
    data_emissao = models.DateField()
    valor_total_pedido = models.DecimalField(max_digits=10, decimal_places=2)
    produtos = models.JSONField()
    parcelas = models.JSONField()
    adiantado = models.BooleanField(default=False)

    def __str__(self):
        return f"Pedido {self.numero_pedido}"

    @classmethod
    def criar_de_api(cls, dados_venda):
        try:

            numero_pedido = dados_venda['cabecalho']['numero_pedido']
            codigo_pedido = dados_venda['cabecalho']['codigo_pedido']
            numero_pedido_cliente = dados_venda['informacoes_adicionais']['numero_pedido_cliente']

            if 'lista_parcelas' not in dados_venda or 'parcela' not in dados_venda['lista_parcelas']:
                raise ValueError(
                    "Dados de parcelas ausentes nos dados da venda")
            data_vencimento = dados_venda['lista_parcelas']['parcela'][0]['data_vencimento']
            data_vencimento_iso = datetime.strptime(
                data_vencimento, '%d/%m/%Y').date()

            data_emissao_br = dados_venda['infoCadastro']['dInc']
            data_emissao_iso = datetime.strptime(
                data_emissao_br, '%d/%m/%Y').date()

            valor_total_pedido = dados_venda['total_pedido']['valor_total_pedido']

            produtos = [{
                'valor': produto['produto']['valor_unitario'],
                'descricao': produto['produto']['descricao'],
                'codigo': produto['produto']['codigo']
            } for produto in dados_venda['det']]

            parcelas = dados_venda['lista_parcelas']['parcela']

            etapa = int(dados_venda['cabecalho']['etapa'])
            adiantado = etapa > 30

            if not adiantado:
                adiantado = any(parcela.get('parcela_adiantamento')
                                == 'S' for parcela in parcelas)

            return cls(
                numero_pedido=numero_pedido,
                codigo_pedido=codigo_pedido,
                numero_pedido_cliente=numero_pedido_cliente,
                data_vencimento=data_vencimento_iso,
                data_emissao=data_emissao_iso,
                valor_total_pedido=valor_total_pedido,
                produtos=produtos,
                parcelas=parcelas,
                adiantado=adiantado
            )
        except KeyError as e:
            raise ValueError(f"Dado obrigatório não encontrado: {e}")
