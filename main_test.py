import asyncio
from binance import AsyncClient, BinanceSocketManager
import pandas as pd
from dotenv import load_dotenv
import os

from src.data.feed_handler import parse_payload
from src.strategies.random_test import random_test_strategy
from src.execution.executor import execute_order

load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_SECRET_KEY")


class Bot: 
    def __init__(self, data_handler, strategy, execution):
        self.data_handler = data_handler
        self.strategy = strategy
        self.execution = execution

    async def on_market_data(self, client, payload):
        # Parse the payload
        time, price = self.data_handler(payload)           

        print(f"Time: {time} | Price: {price}")         

        # Get trade signal depending on chosen strategy
        trade_signal = self.strategy(price)      

        # Send trade signal to execution
        if trade_signal != "HOLD":                     
            await self.execution(
                client, 
                symbol="BTCUSDT",           # Hard coded while testing
                trade_signal=trade_signal, 
                quantity=0.01               # Hard coded while testing
            )      
    

async def main():
    # Initliase Binance client 
    client = await AsyncClient.create(api_key, api_secret, testnet=True)

    # Set up the Binance socket. Using miniticker_socker for just current price - it gives 24h OHLCV. For other intervals, use Kline. 
    bm = BinanceSocketManager(client)
    ts = bm.symbol_miniticker_socket(symbol="BTCUSDT")  

    # Declaring which functions handle each module
    data_handler = parse_payload
    strategy = random_test_strategy
    execution = execute_order

    # Instantiating the object
    bot = Bot(data_handler, strategy, execution)

    # Main event loop
    try:
        async with ts as tscm: 
            while True:
                response = await tscm.recv()
                await bot.on_market_data(client, response)

    finally:
        await client.close_connection()


asyncio.run(main())



