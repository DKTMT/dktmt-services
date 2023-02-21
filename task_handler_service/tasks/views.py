from rest_framework.views import APIView
from rest_framework.response import Response
from tvDatafeed import TvDatafeed, Interval

import json


class StrategyView(APIView):
    def get(self, request):
        response = Response()
        response.data = {
            'strategies': [
                {
                    'name': 'Basic',
                    'sample_params': [
                        {
                            'EMA1' : 200,
                            'EMA2' : 50,
                            'EMA3' : 20,
                        }
                    ]
                },
                {
                    'name': 'MACD',
                    'sample_params': [
                        {
                            'EMA1' : 12,
                            'EMA2' : 26,
                        }
                    ]
                }
            ]
        }
        return response
    
class PredictView(APIView):
    def prediction(self, strategy, params):
        if (strategy == "Basic"):
            # result = basic_predict("BTCUSDT")
            predict = {
                "strategy": strategy,
                "type": "buy",
                "time_frame": 15,
                "date_time": "2022-02-8 16:30:00" 
            }
        elif (strategy == "Basic"):
            predict = {
                "strategy": strategy,
                "type": "buy",
                "time_frame": 15,
                "date_time": "2022-02-8 17:00:00" 
            }
        else:
            predict = {
                "strategy": strategy,
                "type": "buy",
                "time_frame": 15,
                "date_time": "2022-02-8 16:30:00" 
            }

        return predict
        
        
    # predict current situation
    def get(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        
        strategy = body['strategy']
        params = body['params']
        noti = True
        
        response = Response()
        response.data = self.prediction(strategy, params)
        
        return response
    
    # predict nearest coming best timing for buying and sellng