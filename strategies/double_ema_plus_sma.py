import os, sys
sys.path.insert(1, os.path.dirname(__file__) + '/..')

import talib as ta
import numpy as np
import pandas as pd
import vectorbt as vbt
from datetime import datetime
import plotly.express as px

import types_enums.base_strategy_enum as base_strategy_enum

from strategies.base_strategy import BaseStrategy
from handler.backtest_handler import datetime_slicer
from handler.crypto_px_handler import get_crypto_data_df
from types_enums.vbt_enum import *

import warnings
warnings.filterwarnings("ignore")


class DoubleEMAPlusSMA(BaseStrategy):
    def __init__(self, strategy_class: str, strategy_config: str):
        super().__init__(strategy_class=strategy_class, strategy_config=strategy_config)
        self.data_df = get_crypto_data_df(self.symbol, self.resample)
        self.backtest_df = datetime_slicer(self.backtest_time, self.data_df, self.start_date, self.end_date, self.count_to_now)

        # the part you return the prepare_data_param you need in run_backtest
        self.ma_p1 = self._config.get(base_strategy_enum.PREPARE_DATA_PARAM, {}).get("ma_p1", None)
        self.ma_p2 = self._config.get(base_strategy_enum.PREPARE_DATA_PARAM, {}).get("ma_p2", None)

        # the part you return the trading_data_param you need in run_backtest
        self.SL_pct = self._config.get(base_strategy_enum.TRADING_DATA_PARAM, {}).get("SL_pct", None)
        self.TP_pct = self._config.get(base_strategy_enum.TRADING_DATA_PARAM, {}).get("TP_pct", None)
    
    def run_backtest(self):
        super().run_backtest()
        # the part you design backtest trading logic
        # start with self.backtest_df and appending 
        # this is an example of double sma strategy
        # long when ma cross bullish, short in ma cross bearish
        
        # 1. Input the strategy required data
        # SMA
        self.backtest_df['sma_1'] = ta.SMA(self.backtest_df[CLOSE], timeperiod=self.ma_p1)
        self.backtest_df['sma_2'] = ta.SMA(self.backtest_df[CLOSE], timeperiod=self.ma_p2)
        self.backtest_df["prev_sma_1"] = self.backtest_df["sma_1"].shift(1)
        self.backtest_df["prev_sma_2"] = self.backtest_df["sma_2"].shift(1)

        # EMA
        self.backtest_df['ema_1'] = ta.EMA(self.backtest_df[CLOSE], timeperiod=self.ma_p1)
        self.backtest_df['ema_2'] = ta.EMA(self.backtest_df[CLOSE], timeperiod=self.ma_p2)
        self.backtest_df["prev_ema_1"] = self.backtest_df["ema_1"].shift(1)
        self.backtest_df["prev_ema_2"] = self.backtest_df["ema_2"].shift(1)


        # 2. Using the Preparation data to define logic 
        # long
        UP_PERMUTE = (self.backtest_df['ema_1'] > self.backtest_df['ema_2']) & (self.backtest_df['ema_2'] > self.backtest_df['sma_1']) & (self.backtest_df['sma_1'] > self.backtest_df['sma_2'])
        SMA1_CROSSUP_EMA2 = (self.backtest_df['prev_ema_2'] >= self.backtest_df['prev_sma_1']) & (self.backtest_df['ema_2'] < self.backtest_df['sma_1'])

        # short
        DOWN_PERMUTE = (self.backtest_df['ema_1'] < self.backtest_df['ema_2']) & (self.backtest_df['ema_2'] < self.backtest_df['sma_1']) & (self.backtest_df['sma_1'] < self.backtest_df['sma_2'])
        EMA2_CROSSUP_SMA1 = (self.backtest_df['prev_ema_2'] <= self.backtest_df['prev_sma_1']) & (self.backtest_df['ema_2'] > self.backtest_df['sma_1'])

        # 3. Define the Long/Short in Entry/Exit 
        self.backtest_df['entry_long'] = np.where(UP_PERMUTE, True, False)
        self.backtest_df['entry_short'] = np.where(DOWN_PERMUTE, True, False)
        self.backtest_df['exit_long'] = np.where(SMA1_CROSSUP_EMA2, True, False)
        self.backtest_df['exit_short'] = np.where(EMA2_CROSSUP_SMA1, True, False) 

        # 4. Generate the backtest result
        self.generate_backtest_result()