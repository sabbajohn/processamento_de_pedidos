import os
import sys
import time
import datetime
import requests
import json
#320fc803-e72a-46a5-a23a-2f189abb8a8c
class LeroyMerlin(object):
    
    def __init__(self):
        self.url = 'https://api-dev.leroymerlin.com.br/v1/marketplace'
        self.apiKey = '320fc803-e72a-46a5-a23a-2f189abb8a8c'
        
    def confirmarEnvio(self,order_id):
        route = "/orders/{}/ship?shop_id".format(order_id)
        payload={}
        headers = {
        'ApiKey': self.apiKey,
        'Accept': '*/*'
        }

        response = requests.request("PUT", self.url+route, headers=headers, data=payload)
        return response

    def infoRastreio(self, order_info, rastreio):
        route = "/orders/{}/tracking?shop_id".format(order_id)
        payload = json.dumps({
            "carrier_name": rastreio,
            "carrier_url": rastreio,
            "tracking_number": rastreio
            })
        headers = {
            'ApiKey': self.apiKey,
            'Accept': '*/*',
            'Content-Type': 'application/json'
            }
        response = requests.request("PUT", self.url+route, headers=headers, data=payload)
        return response