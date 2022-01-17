import datetime
import time
from time import sleep
import json

REQ_MAX = 40
class Alimentador(object):

    def alimentaFila(M):
        while True:
            if M.nRequisicoes < REQ_MAX:
                M.buscarPedidosAprovados()
                sleep(120)

    def defineStatus(M):
        while True:
            if M.nRequisicoes < REQ_MAX:
                processados = {}    
                pendentes = M.db.load("PENDENTES")
                if pendentes:
                    for pedido in pendentes:
                        if M.nRequisicoes < REQ_MAX:
                            if pedido_detalhado := M.buscarPedidoDetalhado(pedido, 'json'):
                                pedido_detalhado['pedido']['sys_info'] = dict()
                                status = M.AnalisaPedido(pedido_detalhado['pedido'])
                                if status == "GERAR":
                                    # Gerar e emitir nota!
                                    parametro_k = "{}_{}".format(status, pedido)
                                    pedido_detalhado['pedido']['sys_info']['hora_processamento'] = str(datetime.datetime.now())
                                    M.db.save(parametro_k, pedido_detalhado['pedido'])
                                elif "2H" in status:
                                    parametro_k = "{}_{}_{}".format(status,pedido, pedido_detalhado['pedido']['cliente']['cpf_cnpj'])
                                    pedido_detalhado['pedido']['sys_info']['hora_processamento'] = str(datetime.datetime.now())
                                    M.db.save(parametro_k, pedido_detalhado['pedido'])
                                elif "NPAGO" in status:
                                    parametro_k = "{}_{}".format(status, pedido)
                                    pedido_detalhado['pedido']['sys_info']['hora_processamento'] = str(datetime.datetime.now())
                                    M.db.save(parametro_k, pedido_detalhado['pedido'])
                                elif status == "CNPJ":
                                    parametro_k = "{}_{}".format(status, pedido)
                                    pedido_detalhado['pedido']['sys_info']['hora_processamento'] = str(datetime.datetime.now())
                                    M.db.save(parametro_k, pedido_detalhado['pedido'])
                                elif status == "OUTLET":
                                    parametro_k = "{}_{}".format(status, pedido)
                                    M.db.save(parametro_k, pedido_detalhado['pedido'])
                                processados[pedido] = pendentes[pedido]
                            else:
                                continue
                    value = { k : pendentes[k] for k in set(pendentes) - set(processados) }
                    M.db.save("PENDENTES", value)
                    nosistema = M.db.load("PROCESSADOS") if M.db.load("PROCESSADOS") else dict()
                    todosprocessados = {**nosistema, **processados}
                    M.db.save("PROCESSADOS",todosprocessados)
                    sleep(30)