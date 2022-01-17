import datetime
import time
from time import sleep
import json

REQ_MAX = 40
class Notas(object):
    
    def aGerarNota(M):
        while True:
            keys = M.db.loadKeys("GERAR*")
            for k in keys:
                pedido = M.db.load(k)
                idPedido = k.split('_')[1]
                if M.nRequisicoes < REQ_MAX:
                    response = M.gerarNfe(idPedido, 'nfe', 'json')
                else:
                    break
                #TODO enviar email ao SAC
                
                if response:
                    try:
                        pedido['sys_info']['nfe'] = response['registros']['registro']
                    except Exception as e:
                        pass
                    M.db.save(k, pedido)
                    parametro_k = "EMITIR_NF_{}".format(idPedido)
                    M.db.rename(k,parametro_k)
                else:
                    # TODO: Registra erro e me notifica
                    pass

    def emitirNota(M):
        while True:
            keys = M.db.loadKeys("EMITIR_NF_*")
            for k in keys:
                pedido = M.db.load(k)
                idPedido = k.split('_')[2]
                if M.nRequisicoes < REQ_MAX:
                    try:
                        nfe = pedido['sys_info']['nfe']
                    except Exception as e:
                        # TODO: Erro, não foi registrado os dados da nota
                        continue
                    response = M.emitirNfe(nfe['idNotaFiscal'], 'json', serie = nfe['serie'], numero = nfe['numero'], enviarEmail = 'N')
                else:
                    continue
                #TODO enviar email ao SAC
                
                if response:
                    pedido['sys_info']['nfe']['nota_fiscal'] = response['nota_fiscal']
                    M.db.save(k, pedido)
                    parametro_k = "NOTIFICAR_{}".format(pedido['id'])
                    M.db.rename(k,parametro_k)
                else:
                    # TODO: Registra erro e me notifica
                    pass