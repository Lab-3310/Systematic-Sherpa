import os
import sys

sys.path.insert(1, f"{os.getcwd()}/..")

from backoffice.vbt_plot.candle import candle_graph

def main():
    symbols = ["BTC-USD"]
    candle_graph(symbols)
    print('here')


if __name__ == '__main__':
    main()