from .exceptions import IdentifierError
from .numeric_identifier import NumericIdentifier


class IdentifierLuhn(NumericIdentifier):

    def __init__(self, last_identifier):
        if last_identifier:
            if not self.is_luhn_valid(last_identifier):
                raise IdentifierError('Invalid identifier, checksum failed. Got {}.'.format(last_identifier))
            self.last_identifier = last_identifier[:-1]
            self.identifier = last_identifier
            self.is_luhn_valid(last_identifier)
        else:
            self.identifier = self.increment()
        check_digit = self.calculate_luhn(self.identifier)
        self.identifier = '{}{}'.format(self.identifier, check_digit)
        if not self.is_luhn_valid(self.identifier):
            raise IdentifierError('Invalid identifier, checksum failed. Got {}.'.format(self.identifier))

    def luhn_checksum(self, identifier):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(identifier)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = 0
        checksum += sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10

    def is_luhn_valid(self, identifier):
        return self.luhn_checksum(self, identifier) == 0

    def calculate_luhn(self, partial_identifier):
        check_digit = self.luhn_checksum(int(partial_identifier) * 10)
        return check_digit if check_digit == 0 else 10 - check_digit
