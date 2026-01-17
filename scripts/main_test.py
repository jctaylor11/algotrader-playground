import asyncio
from binance import AsyncClient, BinanceSocketManager
from binance.exceptions import BinanceAPIException
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_SECRET_KEY")


# random_strategy_cb is the callback function which uses the data stream to execute the strategy
async def random_strategy_cb(client, payload):
    # Printing
    time = pd.to_datetime(payload['E'], unit='ms')
    price = float(payload['c'])
    print(f"Time: {time} | Price: {price}")

    # Random strategy for testing, where it will buy if price is divisible by 10
    if (int(price) % 2 == 0):
        # Safely place older if strategy returns true
        try:
            order = await client.create_order(symbol="BTCUSDT", side="SELL", type="MARKET", quantity=0.1)
            average_buy_price = float(order['cummulativeQuoteQty'])/float(order['executedQty'])
            print(f"BOUGHT at {average_buy_price}")
        except BinanceAPIException as e:
            print(e)

        # Return "STOP" after it buys once, as the condition to stop the bot - main loop is listeniing for 'stop'
        return "STOP" 


async def main():
    client = await AsyncClient.create(api_key, api_secret, testnet=True)
    bm = BinanceSocketManager(client)

    ts = bm.symbol_miniticker_socket(symbol="BTCUSDT")

    try:
        async with ts as tscm: 
            while True:
                response = await tscm.recv()
                strategy = await random_strategy_cb(client, response)

                # If 'stop' is returned, the strategy stops
                if (strategy == "STOP"):
                    print("Stopping, as per set stop condition")
                    break

    finally:
        await client.close_connection()


asyncio.run(main())




