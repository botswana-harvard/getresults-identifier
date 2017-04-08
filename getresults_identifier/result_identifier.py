from edc_identifier.identifier import Identifier


class ResultIdentifier(Identifier):

    """."""

    name = 'result_identifier'
    identifier_pattern = r'.'

    def __init__(self, prefix=None):
        last_identifier = '{}{}'.format(prefix, '000')
        super(ResultIdentifier, self).__init__(last_identifier)

    def increment(self, identifier):
        prefix = identifier[:-3]
        suffix = identifier[-3:]
        return '{}{}'.format(prefix, str(int(suffix or 0) + 1).zfill(3))
