#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 19:39:30 2020

@author: Lukas Wikander
"""

import numpy as np
import pandas as pd
import requests
import json
import yaml

class MarketAccessor:
    def __init__(self):
        self.type_id_data = pd.read_csv('typeids.csv',names=['index','name','type_id'])
        self.region_id_data = self.fetch_region_id_data()

    def fetch_region_id_data(self):
        df = pd.DataFrame(columns=['name','region_id'])
        url = "https://esi.evetech.net/latest/universe/regions"
        resp = requests.get(url)
        if not resp.ok:
            return df
        url = "https://esi.evetech.net/latest/universe/names"
        resp = requests.post(url, resp.content)
        if not resp.ok:
            return df
        df = pd.DataFrame(json.loads(resp.content))
        del df['category']
        df = df[['name', 'id']]
        df.rename(columns={'id': 'region_id'}, inplace=True)
        return df


    def get_type_id_of(self,item_name):
        for _, row in self.type_id_data.iterrows():
            if row['name'] == item_name:
                return row['type_id']
        raise ValueError('Type ID for item "' + str(item_name) + '" not found')


    def get_item_name_of(self,type_id):
        for _, row in self.type_id_data.iterrows():
            if row['type_id'] == type_id:
                return row['name']
        raise ValueError('Name for item ID "' + str(type_id) + '" not found')


    def get_region_id_of(self,region_name):
        for _, row in self.region_id_data.iterrows():
            if row['name'] == region_name:
                return row['region_id']
        raise ValueError('Region ID for region "' + str(region_name) + '" not found')
        

    def get_market_data(self,items=[],region_names=["The Forge"]):
        market_data = pd.DataFrame()
        for item in items:
            for region_name in region_names:
                data = self.send_market_data_request(item, region_name)
                if market_data.empty:
                    market_data = data
                else:
                    market_data = market_data.append(data)
        return market_data

    def send_market_data_request(self,item,region_name):
        df = pd.DataFrame(columns=['item','price','region','range','volume_remain','volume_total','min_volume','type_id','order_id','location_id','system_id','is_buy_order','issued','duration'])
        print("Getting market data from region " + str(region_name) + " for item " + str(item))
        if type(item) is str:
            type_id = self.get_type_id_of(item)
            type_name = item
        else:
            type_id = item
            type_name = self.get_item_name_of(item)
            
        region_id = self.get_region_id_of(region_name)
        page_no = 1
        while True:
            url = "https://esi.evetech.net/latest/markets/"
            url = url + str(region_id)
            url = url + "/orders/?datasource=tranquility&order_type=sell&page="
            url = url + str(page_no) + "&type_id=" + str(type_id)
            resp = requests.get(url)
            if not resp.ok:
                raise requests.RequestException("HTTP request returned status code " + str(resp.status_code) + " for URL " + url)
            json_response = json.loads(resp.content)
            if not json_response:
                break
            else:
                if df.empty:
                    df = pd.DataFrame(json_response)
                else:
                    df = df.append(json_response)
            page_no = page_no + 1
        
        df['region'] = region_name
        df['item'] = type_name
        df = df[['item','price','region','range','volume_remain','volume_total','min_volume','type_id','order_id','location_id','system_id','is_buy_order','issued','duration']]
        return df

class BlueprintDatabase:
    def __init__(self, market_accessor=None):
        if market_accessor:
            self.market_connection = market_accessor
        else:
            self.market_connection = MarketAccessor()
        self.data = pd.DataFrame()

    def load(self,filepath):
        with open(filepath) as file:
            blueprint_data = list(yaml.load(file,Loader=yaml.CLoader).values())
        
        material_map = {self.market_connection.get_type_id_of("Tritanium"): "tritanium_input",
                        self.market_connection.get_type_id_of("Pyerite"): "pyerite_input",
                        self.market_connection.get_type_id_of("Mexallon"): "mexallon_input",
                        self.market_connection.get_type_id_of("Nocxium"): "nocxium_input",
                        self.market_connection.get_type_id_of("Isogen"): "isogen_input",
                        self.market_connection.get_type_id_of("Zydrine"): "zydrine_input",
                        self.market_connection.get_type_id_of("Megacyte"): "megacyte_input",
                        self.market_connection.get_type_id_of("Morphite"): "morphite_input"}
        
        all_data = []
        for blueprint in blueprint_data:
            try:
                data = {}
                data['blueprint_type_id'] = blueprint['blueprintTypeID']
                materials = blueprint['activities']['manufacturing']['materials']
                for known_material in material_map.values():
                    data[known_material] = 0
                for material in materials:
                    data[material_map[material['typeID']]] = material['quantity']
                products = blueprint['activities']['manufacturing']['products']
                if len(products) > 1:
                    print("Blueprint ID " + str(data['blueprint_type_id']) + " produces more than one output")
                data['type_id'] = products[0]['typeID']
                data['produced_quantity'] = products[0]['quantity']
                data['manufacturing_time'] = blueprint['activities']['manufacturing']['time']
                data['copying_time'] = blueprint['activities']['copying']['time']
                all_data.append(data)
            except Exception as e:
                pass
        self.data = pd.DataFrame(all_data)


if __name__ == "__main__":
    accessor = MarketAccessor()
    market_data_frame = accessor.get_market_data(items=["Tritanium","Pyerite"],region_names=["The Forge"])
    print(market_data_frame)
    bp_db = BlueprintDatabase(market_accessor=accessor)
    bp_db.load('sde/fsd/blueprints.yaml')
    market_data_frame = accessor.get_market_data(bp_db.data.iloc[0:3,9])

    print(market_data_frame)

