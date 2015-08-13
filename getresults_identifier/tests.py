from django.test.testcases import TestCase

from .alphanumeric_identifier import AlphanumericIdentifier
from .exceptions import IdentifierError
from .models import IdentifierHistory
from .numeric_identifier import NumericIdentifier, NumericIdentifierWithModulus
from .short_identifier import ShortIdentifier
from getresults_identifier.checkdigit_mixins import LuhnMixin, LuhnOrdMixin, BaseCheckDigitMixin
from getresults_identifier.exceptions import CheckDigitError


class TestIdentifierError(Exception):
    pass


class DummyShortIdentifier(ShortIdentifier):

    history = []
    identifier_pattern = '\w+'

    def update_history(self):
        if self.identifier in self.history:
            raise TestIdentifierError('duplicate {}'.format(self.identifier))
        self.history.append(self.identifier)


class DummyIdentifierWithCheckDigit(LuhnMixin, ShortIdentifier):

    identifier_pattern = '\d+'


class DummyAlphaIdentifierWithCheckDigit(LuhnOrdMixin, ShortIdentifier):

    identifier_pattern = '\w+'


class TestIdentifier(TestCase):

    def test_short_identifier(self):
        short_identifier = ShortIdentifier(options=dict(prefix=22))
        expected_identifier = '{}{}'.format('22', short_identifier.options.get('random_string'))
        self.assertEqual(short_identifier.identifier, expected_identifier)
        self.assertIsInstance(
            IdentifierHistory.objects.get(identifier=expected_identifier),
            IdentifierHistory
        )
        self.assertIsInstance(
            IdentifierHistory.objects.get(identifier=short_identifier.identifier),
            IdentifierHistory
        )
        self.assertIsNotNone(short_identifier.identifier)

    def test_short_identifier_with_last(self):
        last_identifier = '22KVTB4'
        short_identifier = ShortIdentifier(last_identifier=last_identifier)
        expected_identifier = '{}{}'.format('22', short_identifier.options.get('random_string'))
        self.assertEqual(short_identifier.identifier, expected_identifier)
        self.assertNotEqual(short_identifier.identifier, last_identifier)
        self.assertIsInstance(
            IdentifierHistory.objects.get(identifier=expected_identifier),
            IdentifierHistory
        )
        self.assertIsInstance(
            IdentifierHistory.objects.get(identifier=short_identifier.identifier),
            IdentifierHistory
        )
        self.assertIsNotNone(short_identifier.identifier)

    def test_short_identifier_duplicate(self):
        ntries = 0
        max_tries = 10000
        while ntries <= max_tries:
            ntries += 1
            try:
                DummyShortIdentifier(options=dict(prefix=22))
            except TestIdentifierError as e:
                print('Duplicate on {}th attempt. Got {}'.format(ntries, str(e)))
                break
        if ntries >= max_tries:
            print('No duplicate after {} tries'.format(ntries))

    def test_numeric_basic(self):
        NumericIdentifier.identifier_pattern = r'^[0-9]{8}$'
        NumericIdentifier.seed = ('10000000')
        numeric_identifier = NumericIdentifier(None)
        self.assertEqual(numeric_identifier.identifier, '100000017')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '100000025')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '100000033')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '100000041')

    def test_numeric_pattern(self):
        NumericIdentifier.identifier_pattern = r'^[0-9]{10}\-[0-9]{1}$'
        NumericIdentifier.seed = ('1000000008')
        self.assertRaises(IdentifierError, NumericIdentifier, None)

    def test_numeric_seed(self):
        NumericIdentifier.separator = None
        NumericIdentifier.identifier_pattern = r'^[0-9]{10}$'
        NumericIdentifier.seed = ('1999999996')
        instance = NumericIdentifier(None)
        self.assertEqual(instance.identifier, '19999999972')
        instance.next_identifier()
        self.assertEqual(instance.identifier, '19999999980')
        instance.next_identifier()
        self.assertEqual(instance.identifier, '19999999998')
        instance.next_identifier()
        self.assertEqual(instance.identifier, '20000000008')

    def test_numeric_with_last(self):
        NumericIdentifier.separator = None
        NumericIdentifier.identifier_pattern = r'^[0-9]{9}$'
        NumericIdentifier.checkdigit_pattern = r'^[0-9]{1}$'
        NumericIdentifier.seed = ('100000008')
        instance = NumericIdentifier(last_identifier='1999999996')
        self.assertEqual(instance.identifier, '2000000006')

    def test_numeric_separator(self):
        NumericIdentifier.separator = '-'
        NumericIdentifier.identifier_pattern = r'^[0-9]{4}\-[0-9]{4}$'
        NumericIdentifier.checkdigit_pattern = r'^\-[0-9]{1}$'
        NumericIdentifier.seed = '1000-0000'
        numeric_identifier = NumericIdentifier(None)
        self.assertEqual(numeric_identifier.identifier, '1000-0001-7')

    def test_numeric_modulus(self):
        NumericIdentifierWithModulus.separator = '-'
        NumericIdentifierWithModulus.identifier_pattern = r'^[0-9]{4}[0-9]{4}[0-9]{2}$'
        NumericIdentifierWithModulus.checkdigit_pattern = r'^\-[0-9]{2}$'
        NumericIdentifierWithModulus.seed = '1000000010'
        numeric_identifier = NumericIdentifierWithModulus(None)
        self.assertEqual(numeric_identifier.identifier, '1000000011-10')
        self.assertEqual(next(numeric_identifier), '1000000012-11')

    def test_numeric_modulus_with_separator(self):
        NumericIdentifierWithModulus.separator = '-'
        NumericIdentifierWithModulus.identifier_pattern = r'^[0-9]{4}\-[0-9]{4}$'
        NumericIdentifierWithModulus.checkdigit_pattern = r'^\-[0-9]{2}$'
        NumericIdentifierWithModulus.seed = '1000-0000'
        numeric_identifier = NumericIdentifierWithModulus(None)
        self.assertEqual(numeric_identifier.identifier, '1000-0001-11')
        self.assertEqual(next(numeric_identifier), '1000-0002-12')

    def test_split_checkdigit_one(self):
        """Asserts can split identifier with checkdigit into identifier, checkdigit."""
        class DummyIdentifierWithCheckDigit(BaseCheckDigitMixin):

            def calculate_checkdigit(self, identifier):
                return '4'

        mixin = DummyIdentifierWithCheckDigit()
        identifier_with_checkdigit = '987654'
        identifier = mixin.remove_checkdigit(identifier_with_checkdigit)
        checkdigit = identifier_with_checkdigit.replace(identifier, '')
        self.assertEqual(identifier, identifier_with_checkdigit[:-1])
        self.assertEqual(checkdigit, identifier_with_checkdigit[-1:])

    def test_split_checkdigit_two(self):
        """Asserts can split identifier with checkdigit into identifier, checkdigit.

        Tries with a different the checkdigit_pattern"""
        class DummyIdentifierWithCheckDigit(BaseCheckDigitMixin):

            checkdigit_pattern = r'^[0-9]{2}$'

            def calculate_checkdigit(self, identifier):
                return '54'

        mixin = DummyIdentifierWithCheckDigit()
        identifier_with_checkdigit = '987654'
        identifier = mixin.remove_checkdigit(identifier_with_checkdigit)
        checkdigit = identifier_with_checkdigit.replace(identifier, '')
        self.assertEqual(identifier, identifier_with_checkdigit[:-2])
        self.assertEqual(checkdigit, identifier_with_checkdigit[-2:])

    def test_split_checkdigit_exception(self):
        """Asserts raises an exception if cannot split based on the pattern and identifier.

        Note, checkdigit_pattern does not match"""
        class DummyIdentifierWithCheckDigit(BaseCheckDigitMixin):

            checkdigit_pattern = r'^[0-9]{2}$'

            def calculate_checkdigit(self, identifier):
                return '54'

        mixin = DummyIdentifierWithCheckDigit()
        identifier_with_checkdigit = '98765-4'
        self.assertRaises(CheckDigitError, mixin.remove_checkdigit, identifier_with_checkdigit)

    def test_checkdigit(self):
        identifier = 'AAA00007'
        alpha_identifier = AlphanumericIdentifier(identifier)
        identifier_with_checkdigit = alpha_identifier.identifier
        identifier = alpha_identifier.remove_checkdigit(identifier_with_checkdigit)
        checkdigit = identifier_with_checkdigit.replace(identifier, '')
        self.assertEqual(checkdigit, '5')
        self.assertEqual(identifier_with_checkdigit, 'AAA00015')
        alpha_identifier.next()
        self.assertEqual(alpha_identifier.identifier, 'AAA00023')
        alpha_identifier.next()
        self.assertEqual(alpha_identifier.identifier, 'AAA00031')

    def test_alphanumeric(self):
        AlphanumericIdentifier.alpha_pattern = r'^[A-Z]{3}$'
        AlphanumericIdentifier.numeric_pattern = r'^[0-9]{4}$'
        AlphanumericIdentifier.seed = ['AAA', '0000']
        alpha_id = AlphanumericIdentifier(None)
        self.assertEqual(alpha_id.identifier, 'AAA00015')
        self.assertEqual(next(alpha_id), 'AAA00023')
        self.assertEqual(next(alpha_id), 'AAA00031')
        self.assertEqual(next(alpha_id), 'AAA00049')
        self.assertEqual(next(alpha_id), 'AAA00057')
        self.assertEqual(next(alpha_id), 'AAA00065')

    def test_alphanumeric_last(self):
        AlphanumericIdentifier.alpha_pattern = r'^[A-Z]{3}$'
        AlphanumericIdentifier.numeric_pattern = r'^[0-9]{4}$'
        AlphanumericIdentifier.seed = ['AAA', '0000']
        alpha_id = AlphanumericIdentifier('AAA99991')
        self.assertEqual(next(alpha_id), 'AAB00021')
        self.assertEqual(next(alpha_id), 'AAB00039')
        self.assertEqual(next(alpha_id), 'AAB00047')
        self.assertEqual(next(alpha_id), 'AAB00055')
