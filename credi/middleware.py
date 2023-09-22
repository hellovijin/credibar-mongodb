from django.http import JsonResponse

from rest_framework import status

from oauth2_provider.models import Application

class CustomValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        response['Server'] = "Credibar"
        return response
    
    def process_view(self, request, view_func, *args, **kwargs):
        # Check if the 'Your-Header' is present in the request headers
        uri_ = request.resolver_match.url_name.startswith( "api_" )
        if uri_:
            response = {}
            time_zone = request.headers.get('Time-Zone', '')
            if time_zone == '':
                response["message"] = "Your header is missing time zone"
            
            o2_client_id = request.headers.get('Client-Id', '')
            if o2_client_id != '':
                try:
                    instance = Application.objects.get(client_id= o2_client_id)
                except Exception as e:
                    response["message"] = "You don't have permission to access this portal, invalid client id"
            else:
                response["message"] = "Your header is missing client id"

            # Check the value of 'Your-Header'
            if response:
                response["result"] = "failure"
                response = JsonResponse(response, status=status.HTTP_200_OK)
                response['Server'] = "Credibar"
                return response
            # Continue processing the request if header validation passes