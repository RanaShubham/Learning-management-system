import threading
import random
import string
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.template.loader import render_to_string

class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

class Util:
    @staticmethod
    def send_email(user):
        # if flag is not None:
        email_body = 'Hi '+user.name + ' Use the credentials below to login and fill in your details \n' + 'Email:'+user.email+ '\nPassword: password'+'\nThank you,\nTeam LMS'
        data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Login Credentials for LMS'}
        email = EmailMessage(
            subject=data['email_subject'],body=data['email_body'], to=[data['to_email']])
        EmailThread(email).start()


def get_random_password():
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(8))
    print(result_str)
