import os 
import sys
import time
import configparser
import json
import schedule
import xmltodict
import dicttoxml
from services_tbx.processamento_de_pedidos.API.frenet import Frenet
from services_tbx.processamento_de_pedidos.API.tiny import Tiny
from services_tbx.utils.redis_db import RedisDB


class Manage():
    def __init__(self):
        """ 
        Carregar configurações e agendar jobs pelo schedule
        """
        self.Tiny = Tiny()
        self.db = RedisDB()
        self.nRequisicoes = 0
        self.Frenet = Frenet()

    def buscarPedidosAprovados(self):
        # TODO: Tratar eventuais falhas 
        Pedidos = self.Tiny.pesquisa_pedidos("aprovado", "json")
        self.nRequisicoes += 1
        body = json.loads(Pedidos.text)
        aprovados = dict()
        if Pedidos.status_code == 200 and body['retorno']['status'] == 'OK':
            for p in body['retorno']['pedidos']:
                aprovados[p['pedido']['id']] = p['pedido']
            pendentes = self.db.load('PENDENTES') if self.db.load('PENDENTES') else dict()
            processados = self.db.load('PROCESSADOS') if self.db.load('PROCESSADOS') else dict()
            nosistema = {**pendentes, **processados}
            if pendentes:
                value = { k : aprovados[k] for k in set(aprovados) - set(nosistema) }
                todos = {**pendentes, **value}
            else:
                if processados:
                    value = { k : aprovados[k] for k in set(aprovados) - set(processados) }
                    todos = value
                else:
                    todos = aprovados
            self.db.save('PENDENTES', todos)
        
    def buscarPedidoDetalhado(self, id, formato):
        pedido = self.Tiny.obter_pedidos(id, formato)
        self.nRequisicoes += 1
        body = json.loads(pedido.text)
        if pedido.status_code == 200 and body['retorno']['status'] == 'OK':
            return body['retorno']
        else:
            # TODO: Log de erro na criação do pedido
            return False

    #TODO: Efetuar todas as requisições de api por aqui, tratar retorno erros e registrar logs    
    def inserePedido(self, pedido, formato):
        pedido = self.Tiny.incluir_pedido( pedido, formato)
        self.nRequisicoes += 1
        body = json.loads(pedido.text)
        if pedido.status_code == 200 and body['retorno']['status'] == 'OK':
            return body['retorno']
        else:
            # TODO: Log de erro na obtenção do pedido
            return False

    def alteraStatusPedido(self, pedido, status, formato):
        response =  self.Tiny.alterar_situacao_pedidos(pedido, status, formato)
        self.nRequisicoes += 1
        if formato == 'xml':
            body = xmltodict.parse(response.text)
        else:
            body = json.loads(response.text)
        if response.status_code == 200 and body['retorno']['status'] == 'OK':
            return True
        else:
            # TODO: Log de erro na requisição
            return False

    def insereMarcadores(self, id, marcador, formato):
        response = self.Tiny.incluir_marcador(id, marcador, formato)
        self.nRequisicoes += 1
        if formato == 'xml':
            body = xmltodict.parse(response.text)
        else:
            body = json.loads(response.text)
        if response.status_code == 200 and body['retorno']['status'] == 'OK':
            return body['retorno']
        else:
            # TODO: Log de erro na inserção dos marcadores
            return False

    def atualizaLogistica(self, despacho, formato):
        response =  self.Tiny.alterar_informacao_despacho_pedido(despacho, formato)
        self.nRequisicoes += 1
        if formato == 'xml':
            body = xmltodict.parse(response.text)
        else:
            body = json.loads(response.text)
        if response.status_code == 200 and body['retorno']['status'] == 'OK':
            return True
        else:
            # TODO: Log de erro na requisição
            return False

    def obterProduto(self, id, formato):
        response = self.Tiny.obter_produto(id, formato)
        self.nRequisicoes += 1
        if formato == 'xml':
            body = xmltodict.parse(response.text)
        else:
            body = json.loads(response.text)
        if response.status_code == 200 and body['retorno']['status'] == 'OK':
            return body['retorno']['produto']
        else:
            # TODO: Log de erro na requisição
            return False
        

    def gerarNfe(self, idPedido, modelo, formato):
        response = self.Tiny.gerar_Nfe_pedido(idPedido, modelo, formato)
        self.nRequisicoes += 1
        if formato == 'xml':
            body = xmltodict.parse(response.text)
        else:
            body = json.loads(response.text)
        if response.status_code == 200 and body['retorno']['status'] == 'OK':
            return body['retorno']
        else:
            # TODO: Log de erro na requisição
            return False
        pass

    def emitirNfe(self, idNota, formato, serie = None, numero = None, enviarEmail = 'N'):
        response = self.Tiny.emitir_Nfe(idNota, formato, serie = None, numero = None, enviarEmail = 'N')
        self.nRequisicoes += 1
        if formato == 'xml':
            body = xmltodict.parse(response.text)
        else:
            body = json.loads(response.text)
        if response.status_code == 200 and body['retorno']['status'] == 'OK':
            return body['retorno']
        else:
            # TODO: Log de erro na requisição
            return False
        

    def consultaFrenet(self, shipment):
        response = self.Frenet.shipping_quote(shipment)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            #TODO: Log de erros
            return False

    def AnalisaPedido(self,pedido):
        """ Analisa o que será feito com o pedido e como será a sua chave no"""
        """ 
            * Verificações presentes no fluxo grama do Eduardo
                * CPF/CNPJ
                * "nomeEcommerce"
                * "forma_envio"
                * "valor_frete"
            """
        if pedido['cliente']['tipo_pessoa'] =='F':
            # TODO: Tratativas para pessoa fisica
            try:
                pedido['ecommerce']['nomeEcommerce']
                if ("ML" in pedido['ecommerce']['nomeEcommerce']):
                    if (pedido['forma_envio']) == "M":
                        return "GERAR"
                    else:
                        if (float(pedido['valor_frete'])>0.0):
                            return "2H"
                        else:
                            return "NPAGO"
                elif ("SkyHub" in pedido['ecommerce']['nomeEcommerce']):
                    if (pedido['forma_envio']=="B"):
                        return "GERAR"
                    else:
                        if (float(pedido['valor_frete'])>0.0):
                            return "2H"
                        else:
                            return "NPAGO"
                elif ("Integra" in pedido['ecommerce']['nomeEcommerce']):
                    if 'Magalu' in pedido['nome_transportador'] :
                        return "GERAR"
                    else:
                        # if (float(pedido['valor_frete'])>0.0):
                        return "2H"
                elif ("Shopee" in pedido['ecommerce']['nomeEcommerce']):
                    return "GERAR"
                elif ("Leroy" in pedido['ecommerce']['nomeEcommerce']):
                    if (float(pedido['valor_frete'])>0.0):
                        return "2H"
                else:
                    if (pedido['forma_envio']=="B"):
                        return "GERAR"
                    else:
                        if (float(pedido['valor_frete'])>0.0):
                            return "2H"
                        else:
                            return "NPAGO"
            except Exception as e:
                if (pedido['forma_envio']=="B"):
                    return "GERAR"
                else:
                    if (float(pedido['valor_frete'])>0.0):
                        return "2H"
                    else:
                        return "NPAGO"
        else:
            return "CNPJ"
            
    def verificaPedidoAgrupado(self,pedido):
        Agrupado = False
        for marcador in pedido['marcadores']:
                if marcador['marcador']['id'] == '211516':
                    Agrupado = True
        if Agrupado:
            pass
        else:
            return False
        pass
    def ZeraRequisicoes(self):
        self.nRequisicoes = 0