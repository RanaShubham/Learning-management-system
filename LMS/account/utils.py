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
        password = ''.join(store())

        print(password)
        email_body = 'Hi '+user.name + '\nUse the credentials below to login and fill in your details \n' + \
            'Email:'+user.email+ '\nPassword:'+ password+'\nThank you,\nTeam LMS'
        data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Login Credentials for LMS'}
        email = EmailMessage(
            subject=data['email_subject'],body=data['email_body'], to=[data['to_email']])
        EmailThread(email).start()

    @staticmethod
    def send_reset_email(data):
        """[sends email on the basis of set email parameters in registration view, reset password view and check_remider method]
        """
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        EmailThread(email).start()


def get_random_password():
    letters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(letters) for i in range(10))
    return result_str

def store(*values):
    store.values = values or store.values
    return store.values
    
store.values = ()