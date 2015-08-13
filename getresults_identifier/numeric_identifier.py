import re

from .base_identifier import BaseIdentifier
from .exceptions import IdentifierError
from .checkdigit_mixins import LuhnMixin, ModulusMixin


class NumericIdentifier(LuhnMixin, BaseIdentifier):
    """Class for numeric identifier with check digit."""

    identifier_pattern = r'^[0-9]{10}$'
    separator = None
    seed = ('0000000000')

    def __init__(self, last_identifier=None):
        last_identifier = self.remove_checkdigit(last_identifier)
        self.identifier = last_identifier or ''.join(self.seed)
        self.validate_identifier_pattern(self.identifier)
        self.next_identifier()

    def next_identifier(self):
        """Sets the identifier attr to the next identifier.

        Removes the checkdigit if it has one."""
        if re.match(self.identifier_pattern_with_checkdigit, self.identifier):
            self.identifier = self.remove_checkdigit(self.identifier)
        identifier = self.remove_separator(self.identifier)
        identifier = self.increment(identifier)
        checkdigit = self.calculate_checkdigit(identifier)
        identifier = self.insert_separator(identifier, checkdigit)
        self.identifier = self.validate_identifier_pattern(
            identifier, pattern=self.identifier_pattern_with_checkdigit)
        self.update_history()

    @property
    def identifier_pattern_with_checkdigit(self):
        return '{}{}'.format(self.identifier_pattern[:-1], self.checkdigit_pattern[1:])

    def increment(self, identifier):
        """Returns the incremented identifier."""
        if int(identifier) < self.max_numeric(identifier):
            incr = int(identifier) + 1
        elif int(identifier) == self.max_numeric(identifier):
            incr = 1
        else:
            raise IdentifierError('Unexpected numeric sequence. Got {}'.format(identifier))
        frmt = '{{0:0{}d}}'.format(len(identifier))
        identifier = '{}'.format(frmt.format(incr))
        return identifier

    def max_numeric(self, identifier):
        """Returns max value for numeric segment."""
        return int('9' * len(identifier))


class NumericIdentifierWithModulus(ModulusMixin, NumericIdentifier):
    modulus = 13
