from edc_identifier.short_identifier import ShortIdentifier


class RequisitionIdentifier(ShortIdentifier):

    name = 'requisitionidentifier'
    requisition_model = None

    def is_duplicate(self, identifier):
        try:
            self.requisition_model.get(requisition_identifier=identifier)
            return True
        except self.requisition_model.DoesNotExist:
            pass
        return False
