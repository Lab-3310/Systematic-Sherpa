
import os
os.environ['TZ'] = 'Asia/Hong_Kong'
import sys
import platform
import time

if platform.system() == "Darwin":
    sys.path.insert(1, os.path.dirname(__file__) + '/../..')
    time.tzset() # time zone setting

from pathlib import Path
root_path = str(Path.home())
from datetime import datetime
from binance_ccxt.binance_px import binance_loader

if __name__ == '__main__':

    SINCE = datetime(2016, 1, 1)
    TO = datetime.now()
    binance_loader()