from django.test.testcases import TestCase

from .alphanumeric_identifier import NumericIdentifier
from .exceptions import IdentifierError
from .models import IdentifierHistory
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
        NumericIdentifier.seed = ('0000000000')
        numeric_identifier = NumericIdentifier(None)
        self.assertEqual(numeric_identifier.identifier, '0000000001')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '0000000002')

    def test_numeric_pattern(self):
        NumericIdentifier.identifier_pattern = r'^[0-9]{10}\-[0-9]{1}$'
        NumericIdentifier.seed = ('0000000000')
        self.assertRaises(IdentifierError, NumericIdentifier, None)

    def test_numeric_seed(self):
        NumericIdentifier.identifier_pattern = r'^[0-9]{10}$'
        NumericIdentifier.seed = ('1999999999')
        self.assertEqual(NumericIdentifier(None).identifier, '2000000000')

    def test_numeric_with_last(self):
        NumericIdentifier.identifier_pattern = r'^[0-9]{10}$'
        NumericIdentifier.seed = ('0000000000')
        self.assertEqual(NumericIdentifier('1999999999').identifier, '2000000000')

    def test_numeric_delimeter(self):
        NumericIdentifier.delimeter = '-'
        NumericIdentifier.identifier_pattern = r'^[0-9]{4}\-[0-9]{4}\-[0-9]{1}$'
        NumericIdentifier.seed = ('0000-0000-0')
        numeric_identifier = NumericIdentifier(None)
        self.assertEqual(numeric_identifier.identifier, '0000-0000-1')
