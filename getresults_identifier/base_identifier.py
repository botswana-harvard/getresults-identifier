import re

from .exceptions import IdentifierError
from .models import IdentifierHistory


class BaseIdentifier(object):

    history_model = IdentifierHistory
    identifier_pattern = None

    def __init__(self):
        self.identifier = None

    def __repr__(self):
        return '{0.__name__}(\'{1}\')'.format(self.__class__, self.identifier)

    def __str__(self):
        return self.identifier

    def next_identifier(self):
        """Sets the identifier attr to the next identifier."""
        self.identifier = self.increment()

    def increment(self, identifier=None, update_history=None, pattern=None):
        identifier = identifier or self.identifier
        update_history = True if update_history is None else update_history
        pattern = pattern or self.identifier_pattern
        return identifier

    def validate_identifier_pattern(self, identifier, pattern=None):
        pattern = pattern or self.identifier_pattern
        try:
            re.match('{}'.format(pattern), identifier).group()
        except AttributeError:
            raise IdentifierError('Invalid identifier format for pattern {}. Got {}'.format(pattern, identifier))
        return identifier

    def update_history(self, identifier):
        """Updates the history model."""
        try:
            self.history_model.objects.create(
                identifier=identifier,
                identifier_type=self.identifier_type
            )
        except AttributeError:
            pass
