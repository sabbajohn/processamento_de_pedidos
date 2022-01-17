import os
import sys
import time
import datetime
import requests
import configparser
import urllib.parse
import json
class Tiny(object):
    def __init__(self):
        pass
    
    #Pedidos
    def pesquisa_pedidos(self, situacao, formato):
        """ 
        Efetua a busca de todos os pedidos em uma determinada situação 
        ou todos se uma situação não for especificada
        """
        url = "https://api.tiny.com.br/api2/pedidos.pesquisa.php"
        payload={'token': '2540d8bad69e6d85d2c818280cf57fda3d76ab04',
        'formato': formato,
        'situacao': situacao}
        # headers = {'': ''}
        response = requests.request("POST", url, data=payload )
        return response

    
    def obter_pedidos(self, idPedido, formato):
        url = "https://api.tiny.com.br/api2/pedido.obter.php"
        payload={'token': '2540d8bad69e6d85d2c818280cf57fda3d76ab04',
        'formato': formato,
        'id': idPedido}
        # headers = {'': ''}
        response = requests.request("POST", url, data=payload )
        return response

    def alterar_situacao_pedidos(self, idPedido, situacao, formato):
        url = "https://api.tiny.com.br/api2/pedido.alterar.situacao"

        payload={
            'token': '2540d8bad69e6d85d2c818280cf57fda3d76ab04',
            'formato': formato,
            'id': idPedido,
            'situacao': situacao
        }
        files=[]
        headers = {}

        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        return response

    def alterar_informacao_despacho_pedido(self, payload, formato):
        url = "https://api.tiny.com.br/api2/cadastrar.codigo.rastreamento.pedido.php"

        payload['token'] = '2540d8bad69e6d85d2c818280cf57fda3d76ab04',
        payload['formato'] = formato
        files=[]
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        return response

    def incluir_pedido(self, pedido, formato):
        payload = dict()
        url = "https://api.tiny.com.br/api2/pedido.incluir.php"

        payload['token'] = '2540d8bad69e6d85d2c818280cf57fda3d76ab04',
        payload['formato'] = formato
        payload['pedido'] = pedido
        files=[]
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        return response

    #Marcadores
    def incluir_marcador(self, idPedido, marcadores, formato):
        url = "https://api.tiny.com.br/api2/pedido.marcadores.incluir"
        headers = {}
        payload={
                'token': '2540d8bad69e6d85d2c818280cf57fda3d76ab04',
                'idPedido': idPedido,
                'formato': formato,
                'marcadores': marcadores
                }
        response = requests.request("POST", url,headers=headers, data=payload )
        return response

    def remover_marcador(self, idPedido, marcadores, formato):
        url = "https://api.tiny.com.br/api2/pedido.marcadores.incluir"

        if formato =="json":
            payload = 'token=2540d8bad69e6d85d2c818280cf57fda3d76ab04&fomato=json&idPedido={}&marcadores={}'.format(idPedido, urllib.parse.quote_plus(json.dumps(marcadores)))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        else:
            headers = {}
            payload={
                    'token': '2540d8bad69e6d85d2c818280cf57fda3d76ab04',
                    'idPedido': idPedido,
                    'formato': 'xml',
                    'marcadores': marcadores
                    }
        response = requests.request("POST", url,headers=headers, data=payload )
        return response

    #NF-e
    def gerar_Nfe_pedido(self, idPedido, modelo, formato):
        url = "https://api.tiny.com.br/api2/gerar.nota.fiscal.pedido.php"

        payload={'token': '2540d8bad69e6d85d2c818280cf57fda3d76ab04',
        'id': idPedido,
        'modelo': modelo,
        'formato': formato}
        files=[]
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        return response

    def emitir_Nfe(self, idNota, formato, serie = None, numero = None, enviarEmail = 'N'):
        url = "https://api.tiny.com.br/api2/nota.fiscal.emitir.php"

        payload={'token': '2540d8bad69e6d85d2c818280cf57fda3d76ab04',
        'id': idNota,
        'serie': serie,
        'numero': numero,
        'enviarEmail': enviarEmail,
        'formato': formato}
        files=[]
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        return response

    def obter_link_Nfe(self, idNota, formato):
        return response

    def obter_xml_Nfe(self, idNota):
        return response
    
    #Produtos
    def obter_produto(self, idProduto, formato):
        url = "https://api.tiny.com.br/api2/produto.obter.php"

        payload={'token': '2540d8bad69e6d85d2c818280cf57fda3d76ab04',
        'formato': formato,
        'id': idProduto}
        files=[]
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        return response