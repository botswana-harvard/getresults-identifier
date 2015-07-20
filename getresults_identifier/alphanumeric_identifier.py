import re

from .exceptions import IdentifierError
from .numeric_identifier import NumericIdentifier


class AlphanumericIdentifier(NumericIdentifier):

    alpha_pattern = r'^[A-Z]{3}$'
    numeric_pattern = r'^[0-9]{4}$'
    seed = ('AAA', '0000')

    def __init__(self, last_identifier):
        self.identifier_pattern = '{}{}'.format(self.alpha_pattern[:-1], self.numeric_pattern[1:])
        super(AlphanumericIdentifier, self).__init__(last_identifier)

    def increment(self, identifier=None, update_history=None):
        identifier = identifier or self.identifier
        update_history = True if update_history is None else update_history
        identifier = '{}{}'.format(
            self.increment_alpha_segment(identifier),
            self.increment_numeric_segment(identifier)
        )
        if update_history:
            self.update_history(identifier)
        return identifier

    def increment_alpha_segment(self, identifier):
        alpha = self.alpha_segment(identifier)
        numeric = self.numeric_segment(identifier)
        if int(numeric) < self.max_numeric(identifier):
            return alpha
        elif int(numeric) == self.max_numeric(identifier):
            return self._increment_alpha(alpha)
        else:
            raise IdentifierError('Unexpected numeric sequence. Got {}'.format(identifier))

    def increment_numeric_segment(self, identifier):
        return NumericIdentifier.increment(
            self, identifier=self.numeric_segment(identifier), pattern=self.numeric_pattern, update_history=False)

    def alpha_segment(self, identifier):
        segment = identifier[0:len(self.seed[0])]
        return re.match(self.alpha_pattern, segment).group()

    def numeric_segment(self, identifier):
        segment = identifier[len(self.seed[0]):len(self.seed[0]) + len(self.seed[1])]
        return re.match(self.numeric_pattern, segment).group()

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
