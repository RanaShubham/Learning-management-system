import threading
import random
import string
from django.core.mail import EmailMessage
from django.http import HttpResponse

from services.cache import Cache


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Util:
    @staticmethod
    def send_email(user):

        password = ''.join(store())
        Cache.getInstance().set("TOKEN_" + "password" + "_AUTH", password) #caching the password for test cases
        print(password)
        email_body = 'Hi ' + user.name + '\nUse the credentials below to login and fill in your details \n' + \
                     'Email:' + user.email + '\nPassword:' + password + '\nThank you,\nTeam LMS'
        data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Login Credentials for LMS'}
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        EmailThread(email).start()
        # temp_password = HttpResponse()
        # temp_password.__setitem__(header="HTTP_AUTHORIZATION", value= password)
        # response = Response(result, status=status.HTTP_200_OK, content_type="application/json")
        # response.__setitem__(header="HTTP_AUTHORIZATION", value=token)
        # return response

    @staticmethod
    def send_reset_email(data):
        """[sends email on the basis of set email parameters in registration view, reset password view and check_remider method]
        """
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        EmailThread(email).start()

    @staticmethod
    def manage_response(**kwargs):
        """[prepares result dictionary to be sent as response]

        :param kwargs: [mandatory]:[int]response status
                                   [string]response message
                                   [string]log message
                                   [object]logger object
                       [optional]:[dict] data for successful requests
        :return: dictionary containing result
        """
        result = {}
        result['status'] = kwargs['status']
        result['message'] = kwargs['message']

        if kwargs['status'] == True:
            if 'data' in kwargs:
                result['data'] = kwargs['data']
            if 'header' in kwargs:
                result['header'] = kwargs['header']
            kwargs['logger_obj'].debug('validated data: {}'.format(kwargs['log']))
        else:
            kwargs['logger_obj'].error('error: {}'.format(kwargs['log']))
        return result


def get_random_password():
    letters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(letters) for i in range(10))
    return result_str


def store(*values):
    store.values = values or store.values
    return store.values


store.values = ()
