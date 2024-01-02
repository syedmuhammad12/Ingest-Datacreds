import json
from authorization.models import Config
import http.client
from authorization.serializers import ConfigSerializer
from datetime import datetime
import jwt
from users.models import Users
from django.http import HttpResponse
from rest_framework import status

from authorization.views import VerifyTenant
from configuration import config as configiration

class VerifyRouteMiddleware:
    """This is a middleware which will be entered before every other API. 
    Checks if the login info and module to access is passed as parameters properly"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def get_session_time(self, auth_time, tenant):
        token_auth_time= datetime.fromtimestamp(auth_time)
        difference = datetime.now() - token_auth_time
        seconds_in_day = 24 * 60 * 60
        diff_minutes = list(divmod(difference.days * seconds_in_day + difference.seconds, 60))
        expiry_time = Config.objects.using(tenant).filter(config_key="token_exp_time")
        data = ConfigSerializer(expiry_time, many=True).data
        response = 0
        if int(diff_minutes[0]) < int(data[0]['config_value']):
            response = 1
        return response

    def process_view(self, request, view_function, *view_args, **view_kwargs):
        # return None
        request_url = request.get_full_path()
        # exclude the urls in the below dict
        exlude_url = {
            '/auth/auth_post',
            '/healthcheck',
        }
        if request_url not in exlude_url:
            try:
                response_data = {}
                tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
                configiration.Config.CURRENT_ACTIVE_TENANT = tenant
                request_headers = request.headers
                if 'Authorization' in request_headers:
                    if request_headers['Authorization'] == request.META['HTTP_TENANT_CODE'] \
                            and request_url == "/role/list":
                        return None
                    elif request_headers['Authorization'] != request.META['HTTP_TENANT_CODE']:

                        id_token = request_headers['Authorization']
                        if id_token != '':
                            payload = jwt.decode(id_token, None, None)
                            user_name = payload['upn']
                            # The below lines are added to capture the tenant and user id required for the Audit implementation
                            try:
                                import threading
                                threading.currentThread().__setattr__("CURR_USER_EMAIL_ID",user_name)
                                threading.currentThread().__setattr__("CURR_TENANT_ID",VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant())
                            except Exception as e:
                                #print(e)
                                pass
                            user_details = Users.objects.using(tenant).filter(user_email=user_name).count()
                            if user_details == 1:
                                return None
                                # auth_time = payload['auth_time']
                                # result = self.get_session_time(auth_time, tenant)
                                # if result == 0:
                                #     response_data['status'] = status.HTTP_401_UNAUTHORIZED
                                #     response_data['message'] = 'SESSION EXPIRED'
                                #     return HttpResponse(json.dumps(response_data), content_type="application/json",
                                #                         status=status.HTTP_401_UNAUTHORIZED)
                                # else:
                                #   return None
                    else:
                        response_data['status'] = status.HTTP_401_UNAUTHORIZED
                        response_data['message'] = 'INVALID AUTHORIZATION TOKEN'
                        return HttpResponse(json.dumps(response_data), content_type="application/json",
                                            status=status.HTTP_401_UNAUTHORIZED)
                else:
                    response_data['status'] = status.HTTP_401_UNAUTHORIZED
                    response_data['message'] = 'AUTHORIZATION TOKEN MISSING IN HEADERS'
                    return HttpResponse(json.dumps(response_data), content_type="application/json",
                                        status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                return HttpResponse(str(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return None
