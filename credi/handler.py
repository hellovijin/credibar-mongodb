from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        # customizing the default error response structure
        if 'detail' in response.data.keys() and len( response.data ) == 1:
            response.data['result'] = 'failure'
            response.data['message'] = response.data['detail']
            del response.data['detail']
    return response