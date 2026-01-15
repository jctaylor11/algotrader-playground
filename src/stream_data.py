import asyncio
from binance import AsyncClient, BinanceSocketManager

async def trade_stream_sample(): 
    """
    Web socket for streaming live trade data. This is a commented sample for learning purpose, rather than intended for use. 
    From python-binance docs: https://python-binance.readthedocs.io/en/latest/websockets.html.
    This function is called with 'asyncio.run(live_stream())';
    """
    client = await AsyncClient.create()     # Create API client object
    bm = BinanceSocketManager(client)       # Hands that client object to the python-binance 
    
    # Initialise sockets here. ts is the context manager object, which ensures correct management of connection (setup and shutdown)
    # Only one instance of each type is initalised (not started). ts = trade socket, ks = kline socket, ds = depth socket, etc. 
    #ts = bm.trade_socket('BTCUSDT')
    # ds = bm.depth_socket('BTCUSDT')
    ks = bm.kline_socket('BTCUSDT')
    
    # 'with ts as tscm' starts the connection. tscm is the active and context-managed socket. 
    # res stores the messages received from Binance using the recv with the active scocket.
    async with ks as kscm:
        # Loop 50 times only for testing
        for _ in range(10):             # 10 iterations just for testing. Otherwise use while True
            res = await kscm.recv()
            print(res)

    await client.close_connection()
    print("Connection closed")


# Trade socket stream core for a given bm
# Passing bm as an argument to allow for aggregated asynchronous function (otherwise multiple instances of client)
# Using python API web socket information: https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams 
async def trade_stream(bm):
    ts = bm.trade_socket('BTCUSDT')
    async with ts as tscm:
        for _ in range(10):
            res = await tscm.recv()
            print(res)

    
# Kline socket stream core function
async def kline_stream(bm):
    ks = bm.kline_socket('BTCUSDT')
    async with ks as kscm:
        for _ in range(10):
            res = await kscm.recv()
            print(res)


# Returns the trade streams
async def run_trade_stream():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    await trade_stream(bm)
    await client.close_connection()


# Returns the kline streams
async def run_kline_stream():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    await kline_stream(bm)
    await client.close_connection()


# For testing async - This aggregates all streams
async def run_all_streams():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    
    await asyncio.gather(
        trade_stream(bm),
        kline_stream(bm)
    )

    await client.close_connection()


# For testing:
# asyncio.run(run_kline_stream())
# asyncio.run(run_trade_stream())
# asyncio.run(run_all_streams())