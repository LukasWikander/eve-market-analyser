# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import numpy as np

import pandas as pd

import urllib3 as url

import sqlalchemy as sa

import yaml

history_request_data = {}
history_request_data['datasource'] = 'tranquility'
history_request_data['type_id'] = '32772'




forgeRegionID = 10000002

history_url_forge = 'https://esi.evetech.net/latest/markets/' + str(forgeRegionID) + '/history/' 

history_url_req = history_url_forge + '?datasource=' + history_request_data['datasource'] +'&type_id='+  history_request_data['type_id']

df = pd.read_json(history_url_req)
df['type_id'] = int(history_request_data['type_id'])
df['region_id'] = forgeRegionID

engine = sa.create_engine('sqlite:///foo.db')

df.to_sql('market_history', engine, chunksize=1000)

