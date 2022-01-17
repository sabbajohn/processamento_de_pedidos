from .logistica import Logistica
import datetime
import time
from time import sleep
import json
REQ_MAX = 30

class Pedidos(object):

    def processaPedidos(M):
        while True:
            Integra = False
            Processar_logistica = True
            keys=M.db.loadKeys("2H_*")
            if keys:
                for k in keys:
                    pedido = M.db.load(k)
                    if pedido:
                        
                        try:
                            if 'Integra' in pedido['ecommerce']['nomeEcommerce']:
                                Integra = True
                            else:
                                Integra = False
                        except Exception as e:
                            Integra = False
                        
                        horaPedido = datetime.datetime.strptime(pedido['sys_info']['hora_processamento'], '%Y-%m-%d %H:%M:%S.%f') 
                        if(((datetime.datetime.now() - horaPedido).total_seconds() >= 7200) or (Integra) or Pedidos.verificaUnificado(M, pedido)):
                            if M.nRequisicoes < REQ_MAX:
                                if not Integra:
                                    if ids:=Pedidos.verificaMult(M, pedido):
                                        try:
                                            Pedidos.agruparPedidos(M,k,ids)
                                            continue
                                        except Exception as e:
                                            continue
                                produtos = list()
                                for i in pedido['itens']:
                                    prod = M.db.load("PRD_{}".format(i['item']['id_produto'])) 
                                    
                                    if (not prod):
                                        
                                        response = M.obterProduto(i['item']['id_produto'], 'json')
                                        if response:
                                            prod = response
                                            
                                            prod['quantity'] = i['item']['quantidade']
                                            M.db.save("PRD_{}".format(prod['id']), prod)
                                            
                                        else:
                                            #TODO: Log erros
                                            Processar_logistica = False
                                            break

                                        if 'Outlet' in prod['nome']:
                                            M.db.rename(k, "OUTLET_{}".format(pedido['id']))
                                            Processar_logistica = False
                                            break
                                        produtos.append(prod)
                                    else:
                                        if 'Outlet' in prod['nome']:
                                            M.db.rename(k, "OUTLET_{}".format(pedido['id']))
                                            Processar_logistica = False
                                            break
                                            
                                        prod['quantity'] = i['item']['quantidade']
                                        produtos.append(prod)
                                if Processar_logistica:
                                    if(Logistica.defineLogistica(M, pedido, produtos)):
                                        parametro_k = ("GERAR_{}".format(pedido['id']))
                                        M.db.rename(k, parametro_k)
                                    else:
                                        #todo: logs
                                        pass
                                        
                                        sleep(2)
                                else:
                                    continue
                            else:
                                continue
                    else:
                        continue

    def verificaMult(M,pedido):
        
        if Pedidos.verificaUnificado(M, pedido):
            return False
        try:
            if len(pedido['sys_info']['unificar']) :
                return pedido['sys_info']['unificar']
            else:
                return False
        except Exception as e:
            return False

    def verificaUnificado(M,pedido):
        
        try:
            for marcador in pedido['marcadores']:
                if marcador['marcador']['id'] == '211516':
                    return True
            return False
        except Exception as e:
            print(e)
            return False
        return False


    def agruparPedidos(M,chave_ped,ids):
        cpf = chave_ped.split("_")[2]
        pedidos = list()
        itens = list()
        valor_desconto = 0
        valor_frete = 0
        pedido_layout = Pedidos.pedidoLayout()
        pedidos_keys = list()
        pedidos_keys.append(chave_ped)
        for i in ids:
            pedidos_keys.append("2H_{}_{}".format(i,cpf))
        
        for pedido_k in pedidos_keys:
            pedidos.append(M.db.load(pedido_k))
        
        pedido_novo =  {key:value for (key,value) in pedidos[0].items() if (any(l in key for l in pedido_layout))}
        aux = list()
        for pedido in pedidos:
            aux = [x for x in pedido['itens']]
            valor_desconto += float(pedido['valor_desconto'])
            valor_frete += float(pedido['valor_frete'])
            itens = itens + aux
        
        pedido_novo['valor_desconto'] = str(valor_desconto)
        pedido_novo['valor_frete']= str(valor_frete)
        pedido_novo['itens'] = itens
        pedido_novo["numero_ecommerce"] = 'Unificação de Pedidos'
        pedido_novo['marcadores'].append({"marcador":{'descricao':'Pedido Unificado'}})
        payload = {"pedido":pedido_novo}
        # pedido_novo_xml = dicttoxml(pedido_novo)
        if M.nRequisicoes < REQ_MAX:
            response = M.Tiny.incluir_pedido(json.dumps(payload),'json')
        else:
            sleep(5)
            response = M.Tiny.incluir_pedido(json.dumps(payload),'json')
        try:
            response = json.loads(response.text)
        except Exception as e:
            return False
            #Erro na requisição
        if response['retorno']['status'] == 'OK':
            pedido_novo_id = response['retorno']['registros']['registro']['id']
            pedido_novo['sys_info'] = dict()
            pedido_novo['sys_info']['hora_processamento'] = pedidos[0]['sys_info']['hora_processamento']
            parametro_k = "UNI_{}_{}".format(pedido_novo_id,pedido_novo_id)
            M.db.save(parametro_k,pedido_novo)
            marcador_json = dict()
            for pedido in pedidos:
                marcador_json["marcadores"] = [
                                                {
                                                    "marcador": {
                                                        "descricao": "PEDIDO UNIFICADO CODIGO:{}".format(pedido_novo_id)
                                                    }
                                                }
                                            ]
                                
                response_marcador = M.insereMarcadores(pedido['id'], json.dumps(marcador_json), 'json')
                response_cancelamento = M.alteraStatusPedido(pedido['id'], 'cancelado', 'json')
                
                if response_cancelamento:
                    old_key = "2H_{}_{}".format(pedido['id'],cpf)
                    new_key = "UNI_{}_{}".format(pedido['id'],pedido_novo_id)
                    M.db.rename(old_key,new_key)
                else:
                    old_key = "2H_{}_{}".format(pedido['id'],cpf)
                    new_key = "UNI_{}_{}".format(pedido['id'],pedido_novo_id)
                    M.db.rename(old_key,new_key)
        else:
            return False
            #Erro na requisição
    def removeDaFila(M,chave_fila,cpf):
        fila = M.db.load(chave_fila)
        fila.remove(cpf)
        M.db.load(chave_fila,fila)
        return

    def pedidoLayout():
        cliente = {
            "nome": "",
            "codigo": "",
            "nome_fantasia": "",
            "tipo_pessoa": "",
            "cpf_cnpj": "",
            "ie": "",
            "rg": "",
            "endereco": "",
            "numero": "",
            "complemento": "",
            "bairro": "",
            "cidade": "",
            "uf": "",
            "fone": "",
            "email": "",
            "cep": ""
        }
        endereco_entrega = {
            "tipo_pessoa": "",
            "cpf_cnpj": "",
            "endereco": "",
            "numero": "",
            "complemento": "",
            "bairro": "",
            "cep": "",
            "cidade": "",
            "uf": "",
            "fone": "",
            "nome_destinatario": "",
            "ie": ""
        }
        ecommerce = {
            "id": "",
            "numeroPedidoEcommerce": "",
            "numeroPedidoCanalVenda": "",
            "nomeEcommerce": ""
        }
        
        pedido = {
            "data_pedido":  "",
            "data_prevista": "",
            #"numero_ecommerce":"",
            "cliente":cliente,
            "endereco_entrega" :endereco_entrega,
            "itens": list(),
            "marcadores":list(),
            "nome_transportador": "",
            "forma_pagamento": "",
            "frete_por_conta": "",
            "valor_frete": "",
            "valor_desconto": "",
            "numero_ordem_compra": list(),
            #"ecommerce": ecommerce,
            "numero_pedido_ecommerce": "",
            "situacao": "",
            "obs": "",
            "forma_envio": "",
            "forma_frete": ""
        }
        return pedido
