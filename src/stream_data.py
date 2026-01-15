import asyncio
from binance import AsyncClient, BinanceSocketManager

async def live_stream(): 
    """
    Web socket for streaming live trade data - from python-binance docs: https://python-binance.readthedocs.io/en/latest/websockets.html.
    This function is called with 'asyncio.run(live_stream())';
    """
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    # Start any sockets here. 'ts' = trade socket, but it can be e.g depth socket
    ts = bm.trade_socket('BTCUSDT')
    # ds = bm.depth_socket('BTCUSDT')
    
    # Now start receiving messages. tscm = trade socket context manager
    async with ts as tscm:
        # Loop 50 times only for testing
        for _ in range(50): 
            res = await tscm.recv()
            print(res)

    await client.close_connection()
    print("Connection closed")


asyncio.run(live_stream())