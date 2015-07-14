# getresults-identifier

Base classes for identifiers.

Alphanumeric Identifiers
------------------------

	from getresults_identifier import AlpanumericIdentifier

	class MyIdentifier(AlpanumericIdentifier):
	    alpha_pattern = r'^[A-Z]{3}$'
    	numeric_pattern = r'^[0-9]{4}$'
    	SEED = ('AAA', '0000')
		
With the above your identifier will start with 'AAA0001'. For example:

	>>> from getresults_receive.receive_identifier import ReceiveIdentifier
	>>> new_id = MyIdentifier(None)
	>>> print(new_id)
	'AAA0001'

The identifier increments on the numeric sequence then the alpha:

	>>> new_id = MyIdentifier('AAZ9998)
	>>> print(new_id)
	'AAA9999'	

	>>> new_id.increment()
	>>> print(new_id)
	'AAB9999'	

	>>> new_id = MyIdentifier('AAZ9998)
	>>> print(new_id)
	'AAZ9999'	
	>>> new_id.increment()
	>>> print(new_id)
	'ABA0001'	

See `getresults-receive` for sample usage with `settings` and a `History` model.

Short Identifiers
-----------------

Creates a small identifier that is almost unique, for example, across 25 Edc devices in a community. We use these as sample requisition identifiers that are transcribed manually onto a tube from the Edc screen in a household. Once the sample is received at the local lab it is allocated a laboratory-wide unique specimen identifier.

For example:
 
	from .short_identifier import ShortIdentifier
	
	
	class RequisitionIdentifier(ShortIdentifier):
	    
	    identifier_type = 'requisition_identifier'

Or if you prefer not to use the `IdentifierHistory` model:
	from my_app.models import Requisition

	class RequisitionIdentifier(ShortIdentifier):
	
	    identifier_type = 'requisition_identifier'
	    requisition_model = Requisition
	
	    def is_duplicate(self, identifier):
	        try:
	            self.requisition_model.get(requisition_identifier=identifier)
	            return True
	        except self.requisition_model.DoesNotExist:
	            pass
	        return False

		def update_history(self):
			pass
