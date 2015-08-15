import re

from .exceptions import IdentifierError
from .checkdigit_mixins import LuhnOrdMixin
from .numeric_identifier import NumericIdentifier


class AlphanumericIdentifier(LuhnOrdMixin, NumericIdentifier):

    alpha_pattern = r'^[A-Z]{3}$'
    numeric_pattern = r'^[0-9]{4}$'
    seed = ['AAA', '0000']
    separator = None

    def __init__(self, last_identifier=None):
        self.identifier_pattern = '{}{}'.format(self.alpha_pattern[:-1], self.numeric_pattern[1:])
        self.verify_seed()
        super(AlphanumericIdentifier, self).__init__(last_identifier)

    def verify_seed(self):
        """Verifies the class attribute "seed" matches the regular expressions
        of alpha and numeric and adds a checkdigit to the numeric segment."""
        if not isinstance(self.seed, list):
            raise TypeError('Expected attribute seed to be a list. Got {}'.format(self.seed))
        re.match(self.alpha_pattern, self.seed[0]).group()
        re.match(self.numeric_pattern, self.seed[1]).group()

#     @property
#     def identifier_pattern(self):
#         return '{}{}'.format(self.alpha_pattern[:-1], self.numeric_pattern[1:])

#     def next_identifier(self):
#         """Sets the identifier attr to the next identifier.
# 
#         Removes the checkdigit if it has one."""
#         if re.match(self.identifier_pattern_with_checkdigit, self.identifier):
#             self.identifier = self.remove_checkdigit(self.identifier)
#         identifier = self.remove_separator(self.identifier)
#         identifier = self.increment_alphanumeric(identifier)
#         checkdigit = self.calculate_checkdigit(identifier)
#         identifier = self.insert_separator(identifier, checkdigit)
#         self.identifier = self.validate_identifier_pattern(
#             identifier, pattern=self.identifier_pattern_with_checkdigit)
#         self.update_history()

    @property
    def identifier_pattern_with_checkdigit(self):
        return '{}{}'.format(self.identifier_pattern[:-1], self.checkdigit_pattern[1:])

    def increment(self, identifier):
        """Returns the incremented identifier."""
        identifier = '{}{}'.format(
            self.increment_alpha_segment(identifier),
            self.increment_numeric_segment(identifier)
        )
        return identifier

    def increment_alpha_segment(self, identifier):
        """Increments the alpha segment of the identfier."""
        alpha = self.alpha_segment(identifier)
        numeric = self.numeric_segment(identifier)
        if int(numeric) < self.max_numeric(numeric):
            return alpha
        elif int(numeric) == self.max_numeric(numeric):
            return self._increment_alpha(alpha)
        else:
            raise IdentifierError('Unexpected numeric sequence. Got {}'.format(identifier))

    def increment_numeric_segment(self, identifier):
        """Increments the numeric segment of the identifier."""
        numeric = self.numeric_segment(identifier)
        return super().increment(numeric)

    def alpha_segment(self, identifier):
        """Returns the alpha segment of the identifier."""
        segment = identifier[0:len(self.seed[0])]
        return re.match(self.alpha_pattern, segment).group()

    def numeric_segment(self, identifier):
        """Returns the numeric segment of the partial identifier."""
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
