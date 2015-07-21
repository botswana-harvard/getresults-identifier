from getresults_identifier.exceptions import CheckDigitError


class LuhnMixin(object):

    def partial_identifier(self, identifier):
        return identifier[:-1]

    def is_valid_checkdigit(self, identifier):
        return self.is_luhn_valid(identifier)

    def calculate_checkdigit(self, partial_identifier):
        return self.calculate_luhn(partial_identifier)

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


class ModulusMixin(object):

    modulus = 13

    def partial_identifier(self, identifier):
        return identifier[:-2]

    def is_valid_checkdigit(self, identifier):
        try:
            self.checkdigit(identifier)
            return True
        except CheckDigitError:
            return False

    def calculate_checkdigit(self, partial_identifier):
        checkdigit = int(partial_identifier) % self.modulus
        if self.modulus <= 10:
            return str(checkdigit)
        elif self.modulus > 10 and self.modulus <= 100:
            return '{0:02d}'.format(checkdigit)
        else:
            return '{0:03d}'.format(checkdigit)

    def checkdigit(self, identifier):
        checkdigit = identifier.split(self.partial_identifier(identifier))[1]
        if int(self.partial_identifier(identifier)) % self.modulus != int(checkdigit):
            raise CheckDigitError(
                'Invalid checkdigit for modulus {}. Got {} from {}'.format(self.modulus, checkdigit, identifier))
        return checkdigit
