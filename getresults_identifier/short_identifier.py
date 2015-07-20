import random

from getresults_identifier import IdentifierError

from .base_identifier import BaseIdentifier
from .models import IdentifierHistory


class ShortIdentifier(BaseIdentifier):

    identifier_type = 'short_identifier'
    history_model = IdentifierHistory
    identifier_type = 'short'

    def __init__(self, options, template=None, length=None, allowed_chars=None):
        super(ShortIdentifier, self).__init__()
        self.allowed_chars = allowed_chars or 'ABCDEFGHKMNPRTUVWXYZ2346789'
        self.length = length or 5
        self.template = '{prefix}{random_string}'
        self.duplicate_counter = 0
        self.options = options
        self.random_string = self.get_random_string(length=self.length)
        self.options.update({'random_string': self.random_string})
        self.identifier = self.next_on_duplicate(self.create())

    def next_identifier(self):
        self.identifier = self.next_on_duplicate(self.create())

    def is_duplicate(self, identifier):
        """May override with your algorithm for determining duplicates."""
        try:
            self.history_model.objects.get(identifier=identifier)
            return True
        except self.history_model.DoesNotExist:
            pass
        return False

    def create(self):
        """Creates a new almost unique identifier."""
        return self.template.format(**self.options)

    def next_on_duplicate(self, identifier):
        """If a duplicate, create a new identifier."""
        while True:
            if not self.is_duplicate(identifier):
                break
            self.duplicate_counter += 1
            if self.duplicate_counter == len(self.allowed_chars) ** self.length:
                raise IdentifierError(
                    'Unable prepare a unique requisition identifier, '
                    'all are taken. Increase the length of the random string')
            identifier = self.create()
        self.update_history(identifier)
        return identifier

    def get_random_string(self, length):
        """ safe for people, no lowercase and no 0OL1J5S etc."""
        return ''.join([random.choice(self.allowed_chars) for _ in range(length)])
