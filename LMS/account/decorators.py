import json, jwt, os
from services.logging import loggers
from .utils import Util
from django.http import HttpResponse
from rest_framework import status
from services.cache import Cache
from services.encrypt import Encrypt

logger = loggers("log_decorators.log")

def user_login_required(view_func):
    """[gets token and fetches user id verifying active status.
        If everything is proper delegates to the requested view]

    :param view_func:[get/post/put/patch/delete view according to request]
    :return: call to view_func if everything is proper else exception messages and status code.
    """

    def wrapper(request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION')
            decoded_token = Encrypt.decode(token)
            cache_key = Cache.getInstance().get("TOKEN_"+str(decoded_token['id'])+"_AUTH")
            if cache_key and cache_key.decode("utf-8") == token:
                kwargs['userid'] = decoded_token['id']
                kwargs['role'] = decoded_token['role']
                logger.debug('login token verified for user id: {}'.format(kwargs['userid']))
                return view_func(request, *args , **kwargs)
            else:
                result = Util.manage_response(status=False, message='User must be logged in',
                                                log='User must be logged in', logger_obj=logger)
                HttpResponse.status_code = status.HTTP_401_UNAUTHORIZED
                return HttpResponse(json.dumps(result), HttpResponse.status_code)
        except jwt.ExpiredSignatureError as e:
            result = Util.manage_response(status=False, message='Activation has expired. Please generate a new token',
                                          log=str(e), logger_obj=logger)
            HttpResponse.status_code = status.HTTP_401_UNAUTHORIZED
            return HttpResponse(json.dumps(result), HttpResponse.status_code)
        except jwt.exceptions.DecodeError as e:
            result = Util.manage_response(status=False, message='Please provide a valid token',
                                          log=str(e), logger_obj=logger)
            HttpResponse.status_code = status.HTTP_400_BAD_REQUEST
            return HttpResponse(json.dumps(result), HttpResponse.status_code)
        except Exception as e:
            result = Util.manage_response(status=False, message='Some other issue.Please try again',
                                          log=str(e), logger_obj=logger)
            HttpResponse.status_code = status.HTTP_400_BAD_REQUEST
            return HttpResponse(json.dumps(result), HttpResponse.status_code)

    return wrapper
