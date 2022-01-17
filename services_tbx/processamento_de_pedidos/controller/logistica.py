import datetime
import time
from time import sleep
import json

class Logistica(object):

    def retornaNomeTransportadora(nome,descricao,Uf = False, vaso = False):
        Maximo_UF = ['BA','SE','AL','PE','PB','RN','CE','PI','MA']
        Rpa_UF = ['AC', 'AM', 'AP', 'PA', 'RO', 'RR']
        Sul = ['PR','SC', 'RS']

        if any(e in Uf for e in Sul) and vaso:
            return 'ARLETE TRANSPORTES E LOGÍSTICA'
        elif (nome == '3') or (nome =='OWN1' ):
            return 'Jadlog Logística S.A'
        elif 'OWN3' in nome:
            
            if any(e in Uf for e in Maximo_UF):
                return 'MAXIMO OLIVEIRA E SOARES TRANSPORTES EIRELI'
            elif any(e in Uf for e in Rpa_UF):
                return 'R.P.A. TRANSPORTES E LOGISTICA LTDA'
            else:
                return nome
        elif 'OWN4' in nome:
            return 'Aliança Express Transportes Rodoviário Ltda ME'
        elif 'OWN5' in nome:
            return 'ARLETE TRANSPORTES E LOGÍSTICA'
        elif 'OWN8' in nome:
            return 'TRANSPORTADORA OCIANI LTDA'
        elif 'OWN9' in nome:
            return 'MARCOS ROBERTO RAFFO ME'
        elif 'OWN10' in nome:
            return 'TRANSPORTADORA RISSO LTDA'
        elif 'OWN11' in nome:
            if any(e in Uf for e in Maximo_UF):
                return 'MAXIMO OLIVEIRA E SOARES TRANSPORTES EIRELI'
            elif any(e in Uf for e in Rpa_UF):
                return 'R.P.A. TRANSPORTES E LOGISTICA LTDA'
            else:
                return nome
        elif 'OWN12' in nome:
            return 'ARLETE TRANSPORTES E LOGÍSTICA'
        elif 'OWN13' in nome:
            return 'FRIBURGO TRANSPORTE E LOGISTICA LTDA'
        elif 'DAY1' in nome:
            return 'Daytona Express Servicos de Documentos e Encom Urg Ltda'
        elif 'OWN-CUSTOM' in nome:
            return 'JOSE OSVALDO DE OLIVEIRA EIRELI'
        elif 'EXP' in nome:
            return 'TEX COURIER LTDA.'
        elif 'LBL_1' in nome:
            return 'LB LOG TRANSPORTES LTDA'
        elif 'OWNCUSTOM2' in nome:
            return 'BRISTOT ROCHA TRANSPORTES EIRELI ME'
        elif 'EUC' in nome:
            return 'EUCATUR EMPRESA CASCAVEL DE TRANSPORTE E TURISMO LTDA'
        elif '04596' in nome:
            return 'EMPRESA BRASILEIRA DE CORREIOS E TELEGRAFOS'
        elif '04553' in nome:
            return "Sedex"
        else:
            return descricao
            
    def codigoRastreio(transportadora, cpf_cnpj):
        if 'JADLOG' in transportadora:
            link = 'http://www.jadlog.com.br/tracking?cpf={}'.format(cpf_cnpj.replace("-","").replace(".","").replace("/",""))
        else:
            link = 'https://ssw.inf.br/2/ssw_rastreamento_danfe?'
        return link

    def defineLogistica(M, pedido, produtos):
        arlete_vaso = False
        volumes = 0
        shippingItemArray = list()
        try:
            cep_entrega = pedido['endereco_entrega']['cep'].replace("-","").replace(".","")
        except Exception as e:
            cep_entrega = pedido['cliente']['cep'].replace("-","").replace(".","")
        try:
            Uf_entrega = pedido['endereco_entrega']['uf']
        except Exception as e:
            Uf_entrega = pedido['cliente']['uf']
        request = {
            "SellerCEP": "89213125", # Parametrizar cep da empresa
            "RecipientCEP": cep_entrega,
            "ShipmentInvoiceValue": float(pedido['total_produtos']),
            "ShippingServiceCode": None,
            "RecipientCountry": "BR"
        }
        for prd in produtos:
            if 'Vaso' in prd['nome']:
                arlete_vaso = True
            volumes +=int(float(prd['quantity']))
            shippingItemArray.append({
                "Height":   float(prd['alturaEmbalagem']),
                "Length":   float(prd['comprimentoEmbalagem']),
                "Width":    float(prd['larguraEmbalagem']),
                "Quantity": int(float(prd['quantity'])),
                "Weight":   float(prd['peso_bruto']),
                "SKU":      prd["codigo"],
                "Category": prd["categoria"]
            })
        request['shippingItemArray'] = shippingItemArray
        response = M.consultaFrenet(request)
        if response:
            response_body = response
            for resp in response_body['ShippingSevicesArray']:
                if not resp['Error']:
                    frenetResponse = resp
                    break
                else:
                    continue
            try:
                transportadora = Logistica.retornaNomeTransportadora(frenetResponse['ServiceCode'],frenetResponse['ServiceDescription'], Uf_entrega, arlete_vaso)        
                despacho = {
                    'id': pedido['id'],
                    'formaEnvio': 'C' if (('CORREIOS' in transportadora) or ('Sedex' in transportadora)) else 'T',
                    'formaFrete': 'CIF' if ( not 'Jadlog' in transportadora ) else '.package',
                    'dataPrevista':(datetime.datetime.today() + datetime.timedelta(days=int(frenetResponse["DeliveryTime"]))).strftime('%d/%m/%Y'),
                    'transportadora':transportadora, 
                    'urlRastreamento': Logistica.codigoRastreio(frenetResponse['ServiceDescription'],pedido['cliente']['cpf_cnpj']),
                    'codigoRastreamento':pedido['cliente']['cpf_cnpj'].replace("-","").replace(".","").replace("/",""),
                    'volumes':volumes
                }
                if M.atualizaLogistica(despacho, 'json'):
                    pedido['sys_info']['logistica'] = despacho
                    parametro_k = "2H_{}_{}".format(pedido['id'], pedido['cliente']['cpf_cnpj'])
                    M.db.save(parametro_k, pedido)
                    return True
                else:
                    #TODO Registra LOG
                    return False
            except Exception as e:
                return False

        else:
            #TODO : log de erro
            return False

