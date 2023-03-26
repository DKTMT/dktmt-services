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

    def validate_binance_api(self):
        # Define the endpoint and parameters
        endpoint = f'{self.base_url}/account'
        data = { "timestamp": int(round(time.time() * 1000)) }
        headers = {'X-MBX-APIKEY': self.api_key}
        signature = self.get_binance_signature(data)
        params={
            **data,
            "signature": signature,
        }

        # Send the request and check the response status code
        response = requests.get(endpoint, params=params, headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False

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
                        url = f"{self.base_url}/ticker/price?symbol={asset}USDT"
                        response = requests.get(url)
                        response.raise_for_status()
                        real_time_data = response.json()
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