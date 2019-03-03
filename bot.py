#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
import ccxt
import logging
import schedule
import numpy
import talib
from talib import MA_Type

# Settings
symbol = 'BTC/USD'
amount= 1000
timeframe = '1h'
limit = 100
params = {'partial': True}
environment = 'testnet'
api_key = 'Xxxxx-123456789'
api_secret = 'AbCdEfG1234567891011'

logging.basicConfig(level=logging.DEBUG)

class Bot:
    def __init__(self):
        logging.debug("Initializing Robot.")
        self.exchange = ccxt.bitmex({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })
        if 'test' in self.exchange.urls and environment == 'testnet':
            self.exchange.urls['api'] = self.exchange.urls['test']
        
        self.candles = []
        self.time_lock = 0
    
    def get_candles(self):
        since = self.exchange.milliseconds() - (limit-1) * 60 * 60 * 1000
        candles = self.exchange.fetch_ohlcv(symbol, timeframe, since, limit, params)

        for candle in candles:
            logging.info('{}: O: {} H: {} L:{} C:{}'.format(
                self.exchange.iso8601(candle[0]),
                candle[1],
                candle[2],
                candle[3],
                candle[4]))
        
        return candles
    
    def loop(self):
        self.candles = self.get_candles()

        if self.candles[-1][0] != self.time_lock:
            self.strategy(self.candles)
    
    def strategy(self, candles):
        close = numpy.array(list(map(lambda x:x[4], candles)))
        logging.info('close %s', close)
        upper, middle, lower = talib.BBANDS(close, matype=MA_Type.SMA)
        logging.info('upper %s', upper)
        logging.info('lower %s', lower)

        if close[-1] > lower[-1] and close[-2] > lower[-2] and close[-3] < lower[-3]:
            logging.warn('Buy')
            buy_order = self.exchange.create_market_buy_order(symbol, amount)
            logging.info('buy order %s', buy_order)
        
        if close[-1] < upper[-1] and close[-2] < upper[-2] and close[-3] > upper[-3]:
            logging.warn('Sell')
            sell_order = self.exchange.create_market_sell_order(symbol, amount)
            logging.info('sell order %s', sell_order)
    
    def run(self):
        schedule.every(5).seconds.do(self.loop)
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == '__main__':
    bot = Bot()
    bot.run()
