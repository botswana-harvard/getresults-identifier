import re


class IdentifierError(Exception):
    pass


class AlphanumericIdentifier(object):
    alpha_pattern = r'^[A-Z]{3}$'
    numeric_pattern = r'^[0-9]{4}$'
    SEED = ('AAA', '0000')

    def __init__(self, last_identifier):
        self.last_identifier = last_identifier or ''.join(self.SEED)
        try:
            re.match('{}{}'.format(self.alpha_pattern[:-1], self.numeric_pattern[1:]), self.last_identifier).group()
        except AttributeError:
            raise IdentifierError('Invalid identifier format. Got {}'.format(self.last_identifier))
        self.identifier = self.last_identifier
        self.increment()

    def __repr__(self):
        return '{0.__name__}(\'{1}\')'.format(self.__class__, self.identifier)

    def __str__(self):
        return self.identifier

    def increment(self):
        self.last_identifier = self.identifier
        self.identifier = '{}{}'.format(
            self.increment_alpha_segment(self.last_identifier),
            self.increment_numeric_segment(self.last_identifier)
        )

    def increment_numeric_segment(self, identifier):
        numeric = self.numeric_segment(identifier)
        if int(numeric) < self.max_numeric(identifier):
            incr = int(numeric) + 1
        elif int(numeric) == self.max_numeric(identifier):
            incr = 1
        else:
            raise IdentifierError('Unexpected numeric sequence. Got {}'.format(identifier))
        frmt = '{{0:0{}d}}'.format(len(numeric))
        return frmt.format(incr)

    def increment_alpha_segment(self, identifier):
        alpha = self.alpha_segment(identifier)
        numeric = self.numeric_segment(identifier)
        if int(numeric) < self.max_numeric(identifier):
            return alpha
        elif int(numeric) == self.max_numeric(identifier):
            return self.next_alpha(alpha)
        else:
            raise IdentifierError('Unexpected numeric sequence. Got {}'.format(identifier))

    def alpha_segment(self, identifier):
        segment = identifier[0:len(self.SEED[0])]
        return re.match(self.alpha_pattern, segment).group()

    def numeric_segment(self, identifier):
        segment = identifier[len(self.SEED[0]):len(self.SEED[0]) + len(self.SEED[1])]
        return re.match(self.numeric_pattern, segment).group()

    def max_numeric(self, identifier):
        segment = self.numeric_segment(identifier)
        return int('9' * len(segment))

    def next_alpha(self, text):
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


