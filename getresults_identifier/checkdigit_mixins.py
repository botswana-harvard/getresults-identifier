from getresults_identifier.exceptions import CheckDigitError


class LuhnMixin(object):

    def partial_identifier(self, identifier):
        return identifier[:-1]

    def is_valid_checkdigit(self, identifier):
        return self.is_luhn_valid(identifier)

    def calculate_checkdigit(self, partial_identifier):
        return str(self.calculate_luhn(partial_identifier))

    def checkdigit(self, identifier):
        return identifier.split(self.partial_identifier(identifier))[1]

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

    def is_luhn_valid(self, identifier):
        return self.luhn_checksum(identifier) == 0

    def calculate_luhn(self, partial_identifier):
        check_digit = self.luhn_checksum(int(''.join(map(str, self.digits_of(partial_identifier)))) * 10)
        return check_digit if check_digit == 0 else 10 - check_digit


class LuhnOrdMixin(LuhnMixin):
    """Accepts alpha/numeric but is not standard."""
    def digits_of(self, n):
        return [ord(d) for d in str(n)]

    def is_valid_checkdigit(self, identifier):
        return self.calculate_checkdigit(identifier[:-1]) == identifier[-1:]


class ModulusMixin(object):

    modulus = 13

    def partial_identifier(self, identifier):
        return identifier[:-self.length]

    def is_valid_checkdigit(self, identifier):
        try:
            self.checkdigit(identifier)
            return True
        except CheckDigitError:
            return False

    def calculate_checkdigit(self, partial_identifier):
        checkdigit = int(partial_identifier) % self.modulus
        frmt = '{{0:0{}d}}'.format(self.length)
        return frmt.format(checkdigit)

    def checkdigit(self, identifier):
        checkdigit = identifier.split(self.partial_identifier(identifier))[1]
        if int(self.partial_identifier(identifier)) % self.modulus != int(checkdigit):
            raise CheckDigitError(
                'Invalid checkdigit for modulus {}. Got {} from {}'.format(self.modulus, checkdigit, identifier))
        return checkdigit

    @property
    def length(self):
        return len(str((self.modulus - 1) % self.modulus))
