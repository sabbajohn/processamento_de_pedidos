import os
import sys
import time
import datetime
import requests
import json


class Frenet(object):
    def __init__(self):
        pass

    def shipping_quote(self, pedido):
        url = "http://api.frenet.com.br/shipping/quote"

        payload = json.dumps(pedido)
        headers = {
        'Accept': 'application/json',
        'token': '65B83E7FRD693R40FCRBAD1R3B98BD92BB4B',
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        return response
        

    def tracking_info(self):
        pass