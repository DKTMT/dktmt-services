import urllib.parse
import hmac
import hashlib
import time
import requests


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
    
    def fetch_port_history(self, start_time, end_time):
        path = '/sapi/v1/accountSnapshot'
        params = {
            'type': 'SPOT',
            'startTime': start_time,
            'endTime': end_time,
            'limit': 30,
            'recvWindow': 5000,
            'timestamp': int(time.time() * 1000)
        }

        query_string = '&'.join(["{}={}".format(k, v) for k, v in params.items()])
        signature = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

        query_string += '&signature=' + signature

        base_url = 'https://api.binance.com'
        url = base_url + path + '?' + query_string
        header = {
            'X-MBX-APIKEY': self.api_key
        }

        response = requests.get(url, headers=header)

        if response.status_code != 200:
            raise Exception(f"Error fetching portfolio history: {response.text}")

        json_response = response.json()
        return json_response['snapshotVos']
    
    def fetch_exchange_rates(self, assets):
        exchange_rates = {}

        for asset in assets:
            if asset == 'USDT':
                exchange_rates[asset] = 1
                continue

            symbol = f'{asset}USDT'
            path = '/api/v3/ticker/price'
            url = f'https://api.binance.com{path}?symbol={symbol}'

            response = requests.get(url)
            if response.status_code != 200:
                print(f"Error fetching exchange rate for {symbol}: {response.text}")
                continue

            rate = response.json()
            exchange_rates[asset] = float(rate['price'])

        return exchange_rates
    
    def create_order(self, symbol, side, quantity, price):
        timestamp = int(time.time() * 1000)
        endpoint = f'{self.base_url}/order'

        # Prepare the request payload
        payload = {
            'symbol': symbol,
            'side': side,
            'type': 'LIMIT',
            'timeInForce': 'GTC',
            'quantity': quantity,
            'price': price,
            'recvWindow': 5000,
            'timestamp': timestamp,
        }

        # Generate the signature
        query_string = '&'.join(f'{k}={v}' for k, v in payload.items())
        signature = hmac.new(
            bytes(self.api_secret.encode('utf-8')),
            bytes(query_string.encode('utf-8')),
            hashlib.sha256
        ).hexdigest()

        # Add the signature to the request payload
        payload['signature'] = signature

        # Send the request to the Binance API
        headers = {'X-MBX-APIKEY': self.api_key}
        response = requests.post(
            endpoint,
            headers=headers,
            params=payload
        )

        response.raise_for_status()

        return response.json()

    def process_snapshots(self, snapshots):
        unique_assets = set()
        for snapshot in snapshots:
            for balance in snapshot['data']['balances']:
                unique_assets.add(balance['asset'])

        exchange_rates = self.fetch_exchange_rates(unique_assets)

        processed_snapshots = []

        for snapshot in snapshots:
            data = snapshot['data']
            balances = data['balances']

            total_value_usdt = 0
            for balance in balances:
                asset = balance['asset']
                if asset in exchange_rates:
                    total_value_usdt += (float(balance['free']) + float(balance['locked'])) * exchange_rates[asset]

            processed_snapshots.append({
                'type': snapshot['type'],
                'updateTime': snapshot['updateTime'],
                'value': total_value_usdt
            })

        return processed_snapshots