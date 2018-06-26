import datetime
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six

def iso_to_date(date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )
