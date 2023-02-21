from rest_framework.exceptions import AuthenticationFailed

import binance

class BinanceService():
    api_key = ""
    api_secret = ""

    def fetch_assets(self, coin_values):
        try:
            client = binance.Client(self.api_key, self.api_secret)
        except:
            raise AuthenticationFailed('API key expired')
        account = client.get_account()
        port = {
            "coins_possess": [],
            "port_value": 0
        }
        for coin in account['balances']:
            if(float(coin['free'])>0):
                # {'asset': 'BTC', 'free': '0.00000000', 'locked': '0.00000000'}
                asset = coin["asset"]
                if asset in coin_values:
                    free_value = float(coin["free"]) * float(coin_values[asset])
                    locked_value = float(coin["locked"]) * float(coin_values[asset])
                # If we dont have fetch new data
                else:
                    try:
                        real_time_data = client.get_symbol_ticker(symbol=f"{asset}USDT")
                        coin_price = real_time_data["price"]
                    except:
                        if (asset == "USDT"): coin_price = 1
                        else: coin_price = 0
                    
                    # set current coin value to the table
                    
                    coin_values[asset] = coin_price
                    # set value
                    free_value = float(coin["free"]) * float(coin_price)
                    locked_value = float(coin["locked"]) * float(coin_price)
                
                data = {
                    "asset" : asset,
                    "free_amount": float(coin["free"]),
                    "free_value": free_value,
                    "locked_amount": float(coin["locked"]),
                    "locked_value": locked_value,
                }
                port["coins_possess"].append(data)
                port["port_value"] = port["port_value"] + free_value + locked_value
        return port
    
    def fetch_orders(self):
        return []

    def create_order(self, symbol, side, order_type, quantity, price):
        try:
            client = binance.Client(self.api_key, self.api_secret)
        except:
            raise AuthenticationFailed('API key expired')

        try:
            order = client.futures.order_limit(
                symbol=symbol,
                side=side,
                type=order_type,
                quantity=quantity,
                price=price
            )
            return "Order successful: {order}".format(order)
        except Exception as e:
            raise AuthenticationFailed('API key expired')
