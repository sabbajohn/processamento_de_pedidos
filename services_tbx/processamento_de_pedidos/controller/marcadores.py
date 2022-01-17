import datetime
import time
from time import sleep
import json

REQ_MAX = 40
class Marcadores(object):
    def processaMarcadores(M):
        marcadores = ['CNPJ', 'NPAGO', 'OUTLET']
        while True:
            if M.nRequisicoes < REQ_MAX:
                for marcador in marcadores:
                    keys = M.db.loadKeys("{}*".format(marcador))
                    for k in keys:
                        pedido = M.db.load(k)
                        idPedido = k.split('_')[1]
                        if marcador == "NPAGO":
                            marcador_xml = '<marcadores><marcador><descricao>Frete Não Pago</descricao></marcador></marcadores>'
                            response = M.insereMarcadores(idPedido, marcador_xml, 'xml')
                        else:
                            marcador_xml = '<marcadores><marcador><descricao>{}</descricao></marcador></marcadores>'.format(marcador)
                        response = M.insereMarcadores(idPedido, marcador_xml, 'xml')
                        #TODO enviar email ao SAC
                        if response:
                            parametro_k = "OK_{}_{}".format(marcador,idPedido)
                            M.db.rename(k, parametro_k)
                        else:
                            # TODO: Registra erro e me notifica
                            pass

                pass
    def Erros(M):
        pass