from .controller.manage import Manage
from .controller.alimentador import Alimentador
from .controller.fila2H import Fila2H
from .controller.logistica import Logistica
from .controller.marcadores import Marcadores
from .controller.notas import Notas
from .controller.pedidos import Pedidos

import datetime
import time
from time import sleep
import json
import schedule
from threading import Thread, Event

class Runner():
    def __init__(self):
        self.M = Manage()
        Af = Thread(target=Alimentador.alimentaFila, args=(self.M, ), name='AlimentaFila')
        Ds = Thread(target=Alimentador.defineStatus, args=(self.M, ),name='DefineStatus')
        
        marcador= Thread(target=Marcadores.processaMarcadores, args=(self.M,), name='Marcadores')
        fila = Thread(target=Fila2H.monitoraFila2H, args=(self.M,), name='Fila2H')
        ProcessaPedido = Thread(target=Pedidos.processaPedidos, args=(self.M,),name='Pedidos')
        GerarNotas =  Thread(target=Notas.aGerarNota, args=(self.M,),name='GerarNotas')
        EmitirNotas =  Thread(target=Notas.emitirNota, args=(self.M,),name='EmitirNotas')
        #TODO: A cada minuto zerar M.self.nRequisicoes
        self.Jobs = {

            'AlimetarFila':Af,
            'DefineStatus':Ds,
            'Marcadores':marcador,
            'Fila2H':fila,
            'PedidosUnicos':ProcessaPedido,
            'GerarNotas':GerarNotas,
            'EmitirNotas':EmitirNotas
        }
        schedule.every(1).minutes.do(self.M.ZeraRequisicoes).tag("ZerarRequisicoes")
        


    def run(self):
        for job in self.Jobs:
            self.Jobs[job].start()

        while True:
            schedule.run_pending()
            sleep(1)
        pass