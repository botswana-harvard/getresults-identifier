from django.test.testcases import TestCase

from .alphanumeric_identifier import AlphanumericIdentifier
from .exceptions import IdentifierError
from .models import IdentifierHistory
from .numeric_identifier import NumericIdentifier, NumericIdentifierWithModulus
from .short_identifier import ShortIdentifier


class TestIdentifierError(Exception):
    pass


class DummyShortIdentifier(ShortIdentifier):

    history = []
    identifier_pattern = '\w+'

    def update_history(self, identifier):
        if identifier in self.history:
            raise TestIdentifierError('duplicate {}'.format(identifier))
        self.history.append(identifier)


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
        NumericIdentifier.identifier_pattern = r'^[0-9]{10}$'
        NumericIdentifier.seed = ('1000000008')
        numeric_identifier = NumericIdentifier(None)
        self.assertEqual(numeric_identifier.identifier, '1000000016')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '1000000024')

    def test_numeric_pattern(self):
        NumericIdentifier.identifier_pattern = r'^[0-9]{10}\-[0-9]{1}$'
        NumericIdentifier.seed = ('1000000008')
        self.assertRaises(IdentifierError, NumericIdentifier, None)

    def test_numeric_seed(self):
        NumericIdentifier.identifier_pattern = r'^[0-9]{10}$'
        NumericIdentifier.seed = ('1999999996')
        self.assertEqual(NumericIdentifier(None).identifier, '2000000006')

    def test_numeric_with_last(self):
        NumericIdentifier.identifier_pattern = r'^[0-9]{10}$'
        NumericIdentifier.seed = ('1000000008')
        self.assertEqual(NumericIdentifier(last_identifier='1999999996').identifier, '2000000006')

    def test_numeric_delimeter(self):
        NumericIdentifier.delimeter = '-'
        NumericIdentifier.identifier_pattern = r'^[0-9]{4}\-[0-9]{4}\-[0-9]{1}$'
        NumericIdentifier.seed = '1000-0000-9'
        numeric_identifier = NumericIdentifier(None)
        self.assertEqual(numeric_identifier.identifier, '1000-0001-7')

    def test_numeric_modulus(self):
        NumericIdentifierWithModulus.delimeter = '-'
        NumericIdentifierWithModulus.identifier_pattern = r'^[0-9]{4}[0-9]{4}[0-9]{2}$'
        NumericIdentifierWithModulus.seed = '1000000010'
        numeric_identifier = NumericIdentifierWithModulus(None)
        self.assertEqual(numeric_identifier.identifier, '1000000111')
        self.assertEqual(next(numeric_identifier), '1000000212')

    def test_numeric_modulus_with_delimeter(self):
        NumericIdentifierWithModulus.delimeter = '-'
        NumericIdentifierWithModulus.identifier_pattern = r'^[0-9]{4}\-[0-9]{4}\-[0-9]{2}$'
        NumericIdentifierWithModulus.seed = '1000-0000-10'
        numeric_identifier = NumericIdentifierWithModulus(None)
        self.assertEqual(numeric_identifier.identifier, '1000-0001-11')
        self.assertEqual(next(numeric_identifier), '1000-0002-12')

    def test_alphnumeric(self):
        AlphanumericIdentifier.alpha_pattern = r'^[A-Z]{3}$'
        AlphanumericIdentifier.numeric_pattern = r'^[0-9]{4}$'
        AlphanumericIdentifier.seed = ('AAA', '00003')
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
        AlphanumericIdentifier.seed = ('AAA', '00003')
        alpha_id = AlphanumericIdentifier('AAA99997')
        self.assertEqual(next(alpha_id), 'AAB00021')
