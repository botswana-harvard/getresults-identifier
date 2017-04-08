from datetime import datetime

from django.test.testcases import TestCase

from edc_identifier import BatchIdentifier, IdentifierError

from .result_identifier import ResultIdentifier


class TestIdentifierError(Exception):
    pass


class TestIdentifier(TestCase):

    def test_batch_identifier(self):
        date_prefix = datetime.today().strftime('%Y%m%d')
        batch_identifier = BatchIdentifier()
        self.assertTrue(batch_identifier.identifier.startswith(date_prefix))
        self.assertTrue(batch_identifier.identifier.endswith('0001'))
        next(batch_identifier)
        self.assertTrue(batch_identifier.identifier.startswith(date_prefix))
        self.assertTrue(batch_identifier.identifier.endswith('0002'))
        next(batch_identifier)
        self.assertTrue(batch_identifier.identifier.startswith(date_prefix))
        self.assertTrue(batch_identifier.identifier.endswith('0003'))

    def test_batch_identifier_last(self):
        date_prefix = datetime.today().strftime('%Y%m%d')
        batch_identifier = BatchIdentifier(date_prefix + '9998')
        self.assertTrue(batch_identifier.identifier.startswith(date_prefix))
        self.assertTrue(batch_identifier.identifier.endswith('9999'))
        # raise an error since next suffix would be 0000
        self.assertRaises(IdentifierError, next, batch_identifier)

    def test_result_identifier_last(self):
        result_identifier = ResultIdentifier(prefix='ABC12345')
        self.assertTrue(result_identifier, "ABC12345001")
        next(result_identifier)
        self.assertTrue(result_identifier, "ABC12345002")
        next(result_identifier)
        self.assertTrue(result_identifier, "ABC12345003")
        result_identifier = ResultIdentifier(prefix='ABC12345')
        self.assertTrue(result_identifier, "ABC12345004")
