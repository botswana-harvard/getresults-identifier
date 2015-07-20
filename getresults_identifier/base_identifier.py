from .models import IdentifierHistory


class BaseIdentifier(object):

    history_model = IdentifierHistory

    def __init__(self):
        self.identifier = None

    def __repr__(self):
        return '{0.__name__}(\'{1}\')'.format(self.__class__, self.identifier)

    def __str__(self):
        return self.identifier

    def update_history(self, identifier):
        """Updates the history model."""
        try:
            self.history_model.objects.create(
                identifier=identifier,
                identifier_type=self.identifier_type
            )
        except AttributeError:
            pass
