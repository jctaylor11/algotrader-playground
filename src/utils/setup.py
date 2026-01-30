from binance.client import Client
from dotenv import load_dotenv
import os

def initialise_binance_client(testnet=True):
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_SECRET_KEY")

    client = Client(api_key, api_secret, testnet=testnet)

    return client