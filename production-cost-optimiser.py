# -*- coding: utf-8 -*-

from evemarketaccessor import MarketAccessor, BlueprintDatabase
#markets_of_intere



if __name__ == "__main__":
    accessor = MarketAccessor()
    market_data_frame = accessor.get_market_data(items=["Tritanium","Pyerite"],region_names=["The Forge"])
    print(market_data_frame)
    bp_db = BlueprintDatabase(market_accessor=accessor)
    bp_db.load('sde/fsd/blueprints.yaml')
    print(bp_db.data)
    market_data_frame = accessor.get_market_data(bp_db.data.iloc[0:3,9])

    print(market_data_frame)
