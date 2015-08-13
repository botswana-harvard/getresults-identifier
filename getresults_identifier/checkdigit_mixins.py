import re

from getresults_identifier.exceptions import CheckDigitError


class BaseCheckDigitMixin(object):

    checkdigit_pattern = r'^[0-9]{1}$'
    separator = None

    def calculate_checkdigit(self, identifier):
        """Returns the checkdigit given an identifier."""
        raise NotImplementedError()

    def remove_checkdigit(self, identifier_with_checkdigit):
        """Returns a tuple of identifier, less the check digit, and the check digit.

        If you specify identifier_pattern it will re.match the identifier or
        raise an error."""
        identifier = None
        if self.checkdigit_pattern and identifier_with_checkdigit:
            try:
                checkdigit = re.findall(self.checkdigit_pattern[1:], identifier_with_checkdigit)[0]
            except IndexError:
                raise CheckDigitError(
                    'Cannot match check digit for this identifier using pattern {}. Got {}.'.format(
                        self.checkdigit_pattern, identifier_with_checkdigit))
            identifier = identifier_with_checkdigit[:-len(checkdigit)]
            checkdigit = checkdigit.replace(self.separator or '', '')
            if not checkdigit == self.calculate_checkdigit(identifier):
                raise CheckDigitError(
                    'Identifier with check digit {} is invalid. Got identifier {}'.format(
                        checkdigit, identifier_with_checkdigit))
        return identifier

    def is_valid_checkdigit(self, identifier_with_checkdigit):
        try:
            identifier = self.remove_checkdigit(identifier_with_checkdigit)
            checkdigit = identifier_with_checkdigit.replace(identifier, '')
            if int(self.calculate_checkdigit(identifier)) != int(checkdigit):
                raise CheckDigitError(
                    'Invalid checkdigit for modulus {}. Got {} from {}'.format(
                        self.modulus, checkdigit, identifier_with_checkdigit))
            return True
        except CheckDigitError:
            return False


class LuhnMixin(BaseCheckDigitMixin):

    def calculate_checkdigit(self, identifier):
        identifier = identifier.replace(self.separator or '', '')
        return str(self.calculate_luhn(identifier))

    def digits_of(self, n):
        return [int(d) for d in str(n)]

    def luhn_checksum(self, identifier):
        digits = self.digits_of(identifier)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = 0
        checksum += sum(odd_digits)
        for d in even_digits:
            checksum += sum(self.digits_of(d * 2))
        return checksum % 10

#     def is_luhn_valid(self, identifier):
#         return self.luhn_checksum(identifier) == 0

    def calculate_luhn(self, identifier):
        check_digit = self.luhn_checksum(int(''.join(map(str, self.digits_of(identifier)))) * 10)
        return check_digit if check_digit == 0 else 10 - check_digit


class LuhnOrdMixin(LuhnMixin):
    """Accepts alpha/numeric but is not standard."""
    def digits_of(self, n):
        return [ord(d) for d in str(n)]

    def is_valid_checkdigit(self, identifier, checkdigit_length=None):
        checkdigit_length = checkdigit_length or 1
        return self.calculate_checkdigit(identifier[:-checkdigit_length]) == identifier[-checkdigit_length:]


class ModulusMixin(BaseCheckDigitMixin):

    modulus = 13
    checkdigit_pattern = r'^[0-9]{2}$'

    @property
    def length(self):
        return len(str((self.modulus - 1) % self.modulus))

    def is_valid_checkdigit(self, identifier_with_checkdigit):
        try:
            identifier, checkdigit = self.remove_checkdigit(identifier_with_checkdigit)
            if int(self.calculate_checkdigit(identifier)) != int(checkdigit):
                raise CheckDigitError(
                    'Invalid checkdigit for modulus {}. Got {} from {}'.format(
                        self.modulus, checkdigit, identifier_with_checkdigit))
            return True
        except CheckDigitError:
            return False

    def calculate_checkdigit(self, identifier):
        identifier = identifier.replace(self.separator or '', '')
        checkdigit = int(identifier) % self.modulus
        frmt = '{{0:0{}d}}'.format(self.length)
        return frmt.format(checkdigit)
