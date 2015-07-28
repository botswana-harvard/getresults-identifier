import re

from .exceptions import IdentifierError
from .checkdigit_mixins import LuhnOrdMixin
from .numeric_identifier import NumericIdentifier


class AlphanumericIdentifier(LuhnOrdMixin, NumericIdentifier):

    alpha_pattern = r'^[A-Z]{3}$'
    numeric_pattern = r'^[0-9]{4}$'
    checkdigit_pattern = r'^[0-9]{1}$'
    seed = ['AAA', '0000']

    def __init__(self, last_identifier=None):
        self.verify_seed()
        self.identifier_pattern = '{}{}{}'.format(
            self.alpha_pattern[:-1], self.numeric_pattern[1:-1], self.checkdigit_pattern[1:])
        super(AlphanumericIdentifier, self).__init__(last_identifier)

    def verify_seed(self):
        re.match(self.alpha_pattern, self.seed[0]).group()
        re.match(self.numeric_pattern, self.seed[1]).group()
        self.seed[1] = '{}{}'.format(self.seed[1], self.calculate_checkdigit(''.join(self.seed)))

    def increment(self, identifier=None, update_history=None, pattern=None):
        """Returns the incremented identifier."""
        identifier = identifier or self.identifier
        update_history = True if update_history is None else update_history
        pattern = pattern or self.identifier_pattern
        identifier = '{}{}'.format(
            self.increment_alpha_segment(identifier),
            self.increment_numeric_segment(identifier)[:-1]
        )
        identifier = '{}{}'.format(identifier, self.calculate_checkdigit(identifier))
        self.validate_identifier_pattern(identifier, pattern)
        if update_history:
            self.update_history(identifier)
        return identifier

    def increment_alpha_segment(self, identifier):
        """Increments the alpha segment of the identfier."""
        alpha = self.alpha_segment(identifier)
        numeric = self.numeric_segment(identifier)[:-1]
        if int(numeric) < self.max_numeric(numeric):
            return alpha
        elif int(numeric) == self.max_numeric(numeric):
            return self._increment_alpha(alpha)
        else:
            raise IdentifierError('Unexpected numeric sequence. Got {}'.format(identifier))

    def increment_numeric_segment(self, identifier):
        """Increments the numeric segment of the identfier."""
        segment = NumericIdentifier.increment(
            self, identifier=self.numeric_segment(identifier),
            pattern=self.numeric_pattern[:-1] + self.checkdigit_pattern[1:],
            update_history=False)
        return segment

    def alpha_segment(self, identifier):
        """Returns the alpha segment of the identifier."""
        segment = identifier[0:len(self.seed[0])]
        return re.match(self.alpha_pattern, segment).group()

    def numeric_segment(self, identifier):
        """Returns the numeric segment of the partial identifier."""
        segment = identifier[len(self.seed[0]):len(self.seed[0]) + len(self.seed[1])]
        pattern = self.numeric_pattern[:-1] + self.checkdigit_pattern[1:]
        return re.match(pattern, segment).group()

    def _increment_alpha(self, text):
        """Increments an alpha string."""
        letters = []
        letters[0:] = text.upper()
        letters.reverse()
        for index, letter in enumerate(letters):
            if ord(letter) < ord('Z'):
                letters[index] = chr(ord(letter) + 1)
                break
            else:
                letters[index] = 'A'
        letters.reverse()
        return ''.join(letters)
