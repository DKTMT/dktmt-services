from binance_api.models import UserAPI
from binance_api.services import BinanceService
from portfolios.models import Portfolio


def fetch_data_cron_job():
    coin_values = {}
    user_apis = UserAPI.objects.all()
    binance_service = BinanceService()
    
    print ("Cronjob running...")
    for user_api in user_apis:
        binance_service.api_key = user_api.api_key
        binance_service.api_secret = user_api.api_secret
        # Fetch the current value of all coins using the API
        port = binance_service.fetch_assets(coin_values)
    
    # Save the sum and all possess coins to the database
    Portfolio.objects.create(
        hashed_email = user_api.hashed_email,
        port_value = port["port_value"],
        exchange = user_api.exchange,
        coins_possess = port["coins_possess"],
    )