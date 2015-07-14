from django.test.testcases import TestCase

from .models import IdentifierHistory
from .short_identifier import ShortIdentifier


class TestIdentifierError(Exception):
    pass


class DummyShortIdentifier(ShortIdentifier):

    history = []

    def update_history(self):
        if self.identifier in self.history:
            raise TestIdentifierError('duplicate')
        self.history.append(self.identifier)


class TestIdentifier(TestCase):

    def test_short_identifier(self):
        short_identifier = ShortIdentifier(dict(prefix=22))
        expected_identifier = '{}{}'.format('22', short_identifier.random_string)
        self.assertEqual(short_identifier.identifier, expected_identifier)
        self.assertIsInstance(
            IdentifierHistory.objects.get(identifier=expected_identifier),
            IdentifierHistory
        )
        self.assertIsInstance(
            IdentifierHistory.objects.get(identifier=short_identifier.identifier),
            IdentifierHistory
        )

    def test_short_identifier_duplicate(self):
        ntries = 0
        max_tries = 10000
        while ntries <= max_tries:
            ntries += 1
            try:
                DummyShortIdentifier(dict(prefix=22))
            except TestIdentifierError:
                print('Duplicate on {}th attempt'.format(ntries))
                break
        if ntries >= max_tries:
            print('No duplicate after {} tries'.format(ntries))
