import re

from .exceptions import IdentifierError
from .models import IdentifierHistory


class BaseIdentifier(object):

    history_model = IdentifierHistory
    identifier_pattern = None
    separator = None

    def __init__(self):
        self.identifier = None
        self.identifier_as_list = []

    def __repr__(self):
        return '{0.__name__}(\'{1}\')'.format(self.__class__, self.identifier)

    def __str__(self):
        return self.identifier

    def __next__(self):
        self.next_identifier()
        return self.identifier

    def next(self):
        return self.__next__()

    def next_identifier(self):
        """Sets the identifier attr to the next identifier."""
        self.identifier = self.increment()

    def increment(self):
        raise NotImplementedError()

    def validate_identifier_pattern(self, identifier, pattern=None, error_msg=None):
        pattern = pattern or self.identifier_pattern
        error_msg = error_msg or 'Invalid identifier format for pattern {}. Got {}'.format(
            pattern, identifier)
        try:
            identifier = re.match(pattern, identifier).group()
        except AttributeError:
            raise IdentifierError(error_msg)
        return identifier

    def update_history(self):
        """Updates the history model."""
        if self.history_model:
            try:
                self.history_model.objects.create(
                    identifier=self.identifier,
                    identifier_type=self.identifier_type
                )
            except AttributeError:
                pass

    def remove_separator(self, identifier):
        """Returns the identifier after removing the separator and saves the
        items of the identifier as a list."""
        if not identifier:
            return identifier
        else:
            self.identifier_as_list = identifier.split(self.separator)
            return ''.join(self.identifier_as_list)

    def insert_separator(self, identifier, checkdigit=None):
        """Returns the identifier with the separator reinserted using the
        list of identifier "items" from split_on_separator()."""
        if not self.identifier_as_list:
            self.identifier_as_list = [identifier]
        start = 0
        items = []
        for item in self.identifier_as_list:
            items.append(identifier[start:start + len(item)])
            start += len(item)
        if checkdigit:
            items.append(checkdigit)
        identifier = (self.separator or '').join(items)
        return identifier
