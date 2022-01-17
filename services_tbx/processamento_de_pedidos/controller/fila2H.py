import datetime
import time
from time import sleep
import json
from .pedidos import Pedidos
class Fila2H(object):
    #TODO revisar, pedidos multiplos estão sendo processados e não deveriam ser
    def monitoraFila2H(M):
        while True:
            keys = M.db.loadKeys('2H*')
            cpf = list()
            for k in keys:
                cpf.append(k.split("_")[2])
            seen = set()
            uniq = [x for x in cpf if x in seen or seen.add(x)]   
            cpf_multipos =  set(uniq) # Lista de CPF's com multiplos pedidos
            # TODO: encaminhar para agrupar os pedidos
            if len(cpf_multipos):
                Fila2H.validaEndereco(M, cpf_multipos)
            #     mult_fila = M.db.load("PEDIDOS_MULT")
            #     if mult_fila:
            #         cpf_multipos = list(mult_fila) + list(cpf_multipos)
            #     cpf_multipos = set(cpf_multipos) 
            #     M.db.save("PEDIDOS_MULT", list(cpf_multipos))
            #     #LOG PEDIDOS SALVOS NA FILA
            # if len(seen):
            #     unicos_fila = M.db.load("PEDIDOS_UNICOS")
            #     if unicos_fila:
            #         seen = list(set(seen)) + list(set(unicos_fila))
            #         seen = list(set(seen) - set(cpf_multipos))
            #     M.db.save("PEDIDOS_UNICOS", list(seen))
                #LOG PEDIDOS SALVOS NA FILA
            # sleep(60)
    def validaEndereco(M,lista):
        endereco_layout = {
                            "endereco": "",
                            "numero": "",
                            "complemento": "",
                            "bairro": "",
                            "cidade": "",
                            "uf": "",
                            "cep":""
                        }
        for l in lista:
            enderecos = dict()
            end_dif = list()
            pedidos = list()
            keys = M.db.loadKeys('2H_*_{}'.format(l))
            for key in keys:
                pedidos.append(M.db.load(key))
            for pedido in pedidos:
                if pedido:
                    if (Fila2H.verificaUnificado(pedido)):
                        break
                    id_pedido = pedido['id']
                    try:
                        enderecos[pedido['id']] =  {key:value for (key,value) in pedido['endereco_entrega'].items() if (any(l in key for l in endereco_layout))}
                    except Exception as e:
                        enderecos[pedido['id']] =  {key:value for (key,value) in pedido['cliente'].items() if (any(l in key for l in endereco_layout))}
                else:
                    continue
            if not (Fila2H.verificaUnificado(pedido)):
                for id_pedido, endereco in enderecos.items():
                    end_iguais = list()
                    for id_pedido_comp, endereco_comp in enderecos.items():
                        if id_pedido != id_pedido_comp and endereco == endereco_comp:
                            end_iguais.append(id_pedido_comp)
                    pedido_db = M.db.load('2H_{}_{}'.format(id_pedido, l))
                    if pedido_db:
                        pedido_db['sys_info']['unificar'] = end_iguais
                        M.db.save('2H_{}_{}'.format(id_pedido, l), pedido_db)
                    else:
                        continue
            # for id_pedido, endereco in enderecos.items():
                
                
                
    def verificaUnificado(pedido):
            
            try:
                for marcador in pedido['marcadores']:
                    if marcador['marcador']['id'] == '211516':
                        return True
                return False
            except Exception as e:
                print(e)
                return False


                        


                

            
