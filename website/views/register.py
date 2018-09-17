from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.views import View
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from voong_finance.utils import TokenGenerator
from voong_finance.utils.argparse import ArgParser

class RegisterView(View):

    @staticmethod
    def send_email_verification_email(request, email, user):
        subject = 'Verify your email'
        current_site = get_current_site(request)
        domain = current_site.domain
        
        account_activation_token = TokenGenerator()
        body = 'This is a test message sent to {}.\nhttp://{}/activate/{}/{}'.format(
            email,
            domain,
            force_text(urlsafe_base64_encode(force_bytes(user.pk))),
            account_activation_token.make_token(user)
        )
        send_mail(subject, body, 'registration@voong-finance.co.uk', [email, ])

    def post(self, request):

        argparser = ArgParser()
        argparser.add('email', required=True)
        argparser.add('password', required=True)
        args = argparser.parse_args(request, 'POST')
    
        email = args['email']
        password = args['password']
    
        user = User.objects.create_user(username=email, email=email, password=password)
        user.is_active = False

        self.send_email_verification_email(request, email, user)

        user.save()
        return redirect('verify_email')
