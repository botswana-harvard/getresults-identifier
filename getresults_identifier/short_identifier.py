import random

from getresults_identifier import IdentifierError

from .base_identifier import BaseIdentifier
from .models import IdentifierHistory


class ShortIdentifier(BaseIdentifier):

    identifier_pattern = '\w+'
    history_model = IdentifierHistory
    identifier_type = 'short'

    def __init__(self, options, template=None, length=None, allowed_chars=None):
        super(ShortIdentifier, self).__init__()
        self.length = length or 5
        self.duplicate_counter = 0
        self.allowed_chars = allowed_chars or 'ABCDEFGHKMNPRTUVWXYZ2346789'
        self.options = options
        self.template = template or '{prefix}{random_string}'
        self.random_string = self.get_random_string(length=self.length)
        self.options.update({'random_string': self.random_string})
        self.next_identifier()

    def increment(self, identifier=None, update_history=None, pattern=None):
        """Creates a new almost unique identifier."""
        identifier = identifier or self.template.format(**self.options)
        update_history = update_history if update_history is None else update_history
        pattern = pattern or self.identifier_pattern
        identifier = self.next_on_duplicate(identifier)
        self.validate_identifier_pattern(identifier, pattern)
        return identifier

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

    def is_duplicate(self, identifier):
        """May override with your algorithm for determining duplicates."""
        try:
            self.history_model.objects.get(identifier=identifier)
            return True
        except self.history_model.DoesNotExist:
            pass
        return False

    def get_random_string(self, length):
        """ safe for people, no lowercase and no 0OL1J5S etc."""
        return ''.join([random.choice(self.allowed_chars) for _ in range(length)])
