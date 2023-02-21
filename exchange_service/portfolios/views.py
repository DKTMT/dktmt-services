from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from django.forms.models import model_to_dict

from portfolios.models import Portfolio

# Create your views here.
class PortChangesView(APIView):
    def get(self, request):
        port = Portfolio()
        hashed_email = port.hash(request.user_data["email"])

        # check from db
        port_changes = Portfolio.objects.filter(hashed_email=hashed_email)
        if port_changes is None:
            raise AuthenticationFailed('User not found!')

        port_changes_list = [{
            'coins_possess': port_change.coins_possess,
            'port_value': port_change.port_value,
            'created_at': port_change.created_at,
        } for port_change in port_changes]
        
        response = Response()
        response.data = {
            'port_changes': port_changes_list,
            'time_frame': 60
        }
        return response