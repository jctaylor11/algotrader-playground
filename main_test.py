import asyncio
from binance import AsyncClient, BinanceSocketManager
import pandas as pd
from dotenv import load_dotenv
import os

from src.data.feed_handler import parse_ticker
from src.strategies.random_test import random_test_strategy
from src.execution.executor import execute_order

load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_SECRET_KEY")


# random_strategy_cb is the callback function which uses the data stream to execute the strategy
async def random_strategy_cb(client, payload):
    # Parse payload
    time, price = parse_ticker(payload)

    print(f"Time: {time} | Price: {price}")

    # Random strategy for testing, where it will buy if price is divisible by 2
    trade_signal = random_test_strategy(price)

    # Send the trade signal to execution function
    if trade_signal != "HOLD":
        await execute_order(client, symbol="BTCUSDT", trade_signal=trade_signal, quantity=0.01)       # Hard coding symbol and quantity for now while testing


async def main():
    # Initliase Binance client 
    client = await AsyncClient.create(api_key, api_secret, testnet=True)

    # Set up the Binance socket
    bm = BinanceSocketManager(client)
    ts = bm.symbol_miniticker_socket(symbol="BTCUSDT")

    try:
        async with ts as tscm: 
            while True:
                response = await tscm.recv()
                await random_strategy_cb(client, response)

    finally:
        await client.close_connection()


asyncio.run(main())




