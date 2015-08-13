import random
import re

from getresults_identifier import IdentifierError

from .base_identifier import BaseIdentifier
from .models import IdentifierHistory


class ShortIdentifier(BaseIdentifier):

    identifier_type = 'short'
    template = '{prefix}{random_string}'
    prefix_pattern = None
    checkdigit_pattern = None
    random_string_pattern = r'^[A-Z0-9]{5}$'
    allowed_chars = 'ABCDEFGHKMNPRTUVWXYZ2346789'
    history_model = IdentifierHistory

    def __init__(self, last_identifier=None, options=None):
        super(ShortIdentifier, self).__init__()
        self.identifier_pattern = (self.prefix_pattern or '^$')[:-1] + self.random_string_pattern[1:]
        self._options = options or {}
        self.duplicate_counter = 0
        self.last_identifier = last_identifier or None
        self.identifier = last_identifier or None  # only used to update options
        self.next_identifier()

    @property
    def options(self):
        if 'prefix' not in self._options:
            try:
                self._options.update({'prefix': re.match(self.prefix_pattern[:-1], self.last_identifier).group()})
            except TypeError:
                self._options.update({'prefix': ''})
        return self._options

    def next_identifier(self):
        """Sets the identifier attr to the next identifier.

        Removes the checkdigit if it has one."""
        identifier = self.remove_separator(self.identifier)
        identifier = self.increment(identifier)
        identifier = self.insert_separator(identifier)
        self.identifier = self.validate_identifier_pattern(
            identifier, pattern=self.identifier_pattern)
        self.update_history()

    def increment(self, identifier):
        """Creates a new almost unique identifier."""
        return self.next_on_duplicate(identifier)

    def next_on_duplicate(self, identifier):
        """If a duplicate, create a new identifier."""
        length = len(re.match(self.random_string_pattern[:-1], 'A' * 100).group())
        prefix_length = len(re.match(self.random_string_pattern[:-1], 'A' * 100).group())
        while True:
            self.options.update({'random_string': self.get_random_string(length=length)})
            identifier = self.template.format(**self.options)
            if not self.is_duplicate(identifier):
                break
            self.duplicate_counter += 1
            if self.duplicate_counter == len(self.allowed_chars) ** length + prefix_length:
                raise IdentifierError(
                    'Unable prepare a unique requisition identifier, '
                    'all are taken. Increase the length of the random string')
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
