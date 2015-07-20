from .base_identifier import BaseIdentifier
from .exceptions import IdentifierError


class NumericIdentifier(BaseIdentifier):

    identifier_pattern = r'^[0-9]{10}$'
    delimeter = None
    seed = ('0000000000')

    def __init__(self, last_identifier=None):
        super(NumericIdentifier, self).__init__()
        self.identifier = last_identifier or ''.join(self.seed)
        self.validate_identifier_pattern(self.identifier)
        self.next_identifier(self.identifier)

    def increment(self, identifier=None, pattern=None, update_history=None):
        """Returns the incremented identfier."""
        identifier = identifier or self.identifier
        update_history = True if update_history is None else update_history
        pattern = pattern or self.identifier_pattern
        identifier = self.split_segments(identifier)
        if int(identifier) < self.max_numeric(identifier):
            incr = int(identifier) + 1
        elif int(identifier) == self.max_numeric(identifier):
            incr = 1
        else:
            raise IdentifierError('Unexpected numeric sequence. Got {}'.format(identifier))
        frmt = '{{0:0{}d}}'.format(len(identifier))
        identifier = '{}'.format(
            frmt.format(incr)
        )
        identifier = self.join_segments(identifier)
        self.validate_identifier_pattern(identifier, pattern)
        if update_history:
            self.update_history(identifier)
        return identifier

    def max_numeric(self, identifier):
        """Returns max value for numeric segment."""
        return int('9' * len(identifier))

    def split_segments(self, identifier):
        """Returns the segment with the delimeter removed."""
        self.segments = identifier.split(self.delimeter)
        return ''.join(self.segments)

    def join_segments(self, identifier):
        """Returns the segment with the delimeter reinserted."""
        start = 0
        new_segments = []
        for segment in self.segments:
            new_segments.append(identifier[start:start + len(segment)])
            start += len(segment)
        identifier = (self.delimeter or '').join(new_segments)
        return identifier
