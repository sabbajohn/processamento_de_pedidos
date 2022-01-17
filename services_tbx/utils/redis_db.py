#!/usr/bin/python3
# coding: utf-8
import os
import sys
import socket
import logging
import redis
import json

class RedisDB(object):
    def __init__(self):
        self.db: redis.StrictRedis = None
        self.db = self._connect_db()


    def _connect_db(self):
        d = redis.StrictRedis(host='localhost', port=6379, db=1, decode_responses=True)
        cname = "TBX_{}_{}".format(socket.gethostname(), os.getpid())
        d.client_setname(cname)
        # logger.info('[kvdb] connected to persistency db as {}'.format(cname))
        return d

    # def _get_db(self):
    #     return self.db

    def loadKeys(self, parametro_k):
        Keys = self.db.keys("{}".format(parametro_k))
        return Keys
    
    def DelKey(self,key):
        D = self.db.delete(key)
        return D

    def DelMatchKeys(self, keyword):
        keys = self.loadKeys(keyword)
        for k in keys:
            self.DelKey(k)

    def load(self,key):
        o = self.db.get(key)
        if (o):
            data = json.loads(str(o))
            return data
        else:
            return False

    def save(self, parametro_k,data):
        self.db.set(parametro_k, json.dumps(data))

    def rename(self, oldkey, newkey):
        self.db.rename(oldkey, newkey)