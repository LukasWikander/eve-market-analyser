# -*- coding: utf-8 -*-

from evemarketaccessor import MarketAccessor, BlueprintDatabase
import pandas as pd
import time

markets_of_interest=["The Forge","Black Rise","The Citadel","Lonetrek"]
#markets_of_interest=["Black Rise","Lonetrek"]
accessor = MarketAccessor()
accessor.update_market_data(region_names=markets_of_interest)
blueprints = BlueprintDatabase(market_accessor=accessor)
blueprints.load('sde/fsd/blueprints.yaml')

def get_trading_prices_by_region(type_ids):
    trading_prices_all = pd.DataFrame()
    for type_id in type_ids:
        trading_prices_all_regions = pd.DataFrame()
        for market in markets_of_interest:
            market_data_frame = accessor.get_market_data(items=[type_id],region_names=[market])
            try:
                market_data_frame = market_data_frame.sort_values(by=['price'])
                trading_prices_all_regions = trading_prices_all_regions.append(market_data_frame.iloc[0,:])
            except:
                print("Unable to get market data for " + str(type_id) + " from market " + str(market))
        try:
            if not trading_prices_all_regions['price'].isnull().all():
                trading_prices_all_regions = trading_prices_all_regions.sort_values(by=['price'],ascending=False)
                trading_prices_all = trading_prices_all.append(trading_prices_all_regions)
        except KeyError:
            print("No market data for item ID " + str(type_id))
    return trading_prices_all

def find_best_markup(trading_prices, type_ids):
    markup_data = pd.DataFrame()
    for type_id in type_ids:
        type_trading_prices = trading_prices[trading_prices['type_id'] == type_id]
        if type_trading_prices.empty or is_unique(type_trading_prices['region']):
            continue
        type_trading_prices = type_trading_prices.sort_values(by=['price'])
        data_point = {'type_id': type_id, 'buy_price': type_trading_prices['price'].iloc[0],'sell_price': type_trading_prices['price'].iloc[-1:],
                        'buy_location': type_trading_prices['location_id'].iloc[0],'sell_location': type_trading_prices['location_id'].iloc[-1:],
                        'buy_region': type_trading_prices['region'].iloc[0],'sell_region': type_trading_prices['region'].iloc[-1:]}
        data_point['markup'] = data_point['sell_price'] / data_point['buy_price']
        markup_data = markup_data.append(pd.DataFrame(data_point))
    markup_data['item'] = accessor.type_id_map.convert(markup_data['type_id'])
    return markup_data.sort_values(by=['markup'])

def is_unique(s):
    a = s.to_numpy()
    return (a[0] == a).all()

if __name__ == "__main__":
    trading_prices = get_trading_prices_by_region(blueprints.data['type_id'])
    markup_data = find_best_markup(trading_prices, blueprints.data['type_id'])
    pd.set_option('display.max_rows',None)
    markup_data = markup_data[['item','markup','buy_price','sell_price','buy_location','sell_location','buy_region','sell_region','type_id']]
    print(markup_data)

    #market_data_frame = accessor.get_market_data(items=["Tritanium","Pyerite"],region_names=markets_of_interest)
    #print(market_data_frame)
    #print(bp_db.data)
    #market_data_frame = accessor.get_market_data(bp_db.data.iloc[0:3,9])
#
    #print(market_data_frame)
