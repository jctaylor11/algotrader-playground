from binance.exceptions import BinanceAPIException


# Safely place older if strategy returns true
async def execute_order(client, symbol, trade_signal, quantity):
        try:
            order = await client.create_order(symbol=symbol, side=trade_signal, type="MARKET", quantity=quantity)

            average_trade_price = float(order['cummulativeQuoteQty'])/float(order['executedQty'])
            side = order['side']

            print(f"{side} {quantity} {symbol} at {average_trade_price}")
        except BinanceAPIException as e:
            print(e)
