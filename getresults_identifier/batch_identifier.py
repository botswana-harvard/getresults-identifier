from datetime import datetime

from .identifier import Identifier


class BatchIdentifier(Identifier):

    """Manages a sequential identifier prefixed by the current date stamp."""

    name = 'batchidentifier'
    identifier_pattern = r'^[0-9]{4}$'
    prefix_pattern = r'^[0-9]{8}$'
    seed = ['0000']

    def __init__(self, last_identifier=None):
        last_identifier = last_identifier or self.last_identifier
        if not last_identifier:
            prefix = datetime.today().strftime('%Y%m%d')
            last_identifier = '{}{}'.format(prefix, ''.join(self.seed))
        super(BatchIdentifier, self).__init__(last_identifier)
