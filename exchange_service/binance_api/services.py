import urllib.parse
import hmac
import hashlib
import time
import requests
import json


class AuthenticationFailed(Exception):
    pass


class BinanceService():
    base_url = "https://api.binance.com/api/v3"
    api_key = ""
    api_secret = ""

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def get_binance_signature(self, data):
        postdata = urllib.parse.urlencode(data)
        message = postdata.encode()
        byte_key = bytes(self.api_secret, 'UTF-8')
        mac = hmac.new(byte_key, message, hashlib.sha256).hexdigest()
        return mac

    def fetch_assets(self, coin_values):
        # Set up the URL and headers for the API request
        url = f'{self.base_url}/account'
        data = { "timestamp": int(round(time.time() * 1000)) }
        headers = { 'X-MBX-APIKEY': self.api_key }
        signature = self.get_binance_signature(data)
        params={
            **data,
            "signature": signature,
        }

        # Make the API request and check for any errors
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise AuthenticationFailed('API key or secret error') from e

        # Convert the response data to a JSON object
        account = response.json()

        # Initialize the portfolio object
        port = {
            "coins_possess": [],
            "port_value": 0
        }

        # Fetch coin values for assets not in cache
        coins_to_fetch = [coin["asset"] for coin in account["balances"] if float(
            coin["free"]) > 0 and coin["asset"] not in coin_values]
        if coins_to_fetch:
            symbols = [f"{asset}USDT" for asset in coins_to_fetch]
            url = f"{self.base_url}/ticker/price?symbol={'&symbol='.join(symbols)}"
            try:
                response = requests.get(url)
                response.raise_for_status()
                prices = response.json()
                for symbol_price in prices:
                    coin_values[symbol_price["symbol"]
                                     [:-4]] = float(symbol_price["price"])
            except requests.exceptions.RequestException as e:
                pass

        # Loop through each coin in the account balances
        for coin in account['balances']:
            # Only include coins with a positive free balance
            if float(coin['free']) > 0:
                # Get the asset symbol and calculate the free and locked values
                asset = coin["asset"]
                coin_price = coin_values.get(asset, 0)
                free_value = float(coin["free"]) * coin_price
                locked_value = float(coin["locked"]) * coin_price

                # Add the coin data to the portfolio object
                data = {
                    "asset": asset,
                    "free_amount": float(coin["free"]),
                    "free_value": free_value,
                    "locked_amount": float(coin["locked"]),
                    "locked_value": locked_value,
                }
                port["coins_possess"].append(data)

                # Update the portfolio value with the current coin's free and locked values
                port["port_value"] += free_value + locked_value

        # Return the portfolio object
        return port

    def fetch_orders(self):
        # Define the endpoint and parameters
        endpoint = f'{self.base_url}/api/v3/allOrders'
        timestamp = int(time.time() * 1000)
        params = {'timestamp': timestamp}
        headers = {'X-MBX-APIKEY': self.api_key}

        # Generate the signature
        signature_data = urllib.parse.urlencode(params)
        signature_data = signature_data.encode('utf-8')
        signature = self.get_binance_signature(self.api_secret, signature_data)

        # Add the signature to the request parameters
        params['signature'] = signature

        # Send the request and return the response
        response = requests.get(endpoint, params=params, headers=headers)
        return response.json()

    def create_order(self, symbol, side, quantity, price):
        # Define the endpoint and parameters
        endpoint = f'{self.base_url}/api/v3/order'
        timestamp = int(time.time() * 1000)
        params = {
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'type': 'MARKET',
            'timestamp': timestamp,
            'recvWindow': 5000,
        }
        if price is not None:
            params['price'] = price
        headers = {'X-MBX-APIKEY': self.api_key}

        # Generate the signature
        signature_data = urllib.parse.urlencode(params)
        signature_data = signature_data.encode('utf-8')
        signature = self.get_binance_signature(self.api_secret, signature_data)

        # Add the signature to the request parameters
        params['signature'] = signature

        # Send the request and return the response
        response = requests.post(endpoint, params=params, headers=headers)
        return response.json()