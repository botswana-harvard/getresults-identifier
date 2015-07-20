# getresults-identifier

Base classes for identifiers.

Numeric Identifiers
-------------------

	from getresults_identifier import NumericIdentifier

	class MyIdentifier(NumericIdentifier):
		pass
		
	>>> id = MyIdentifier(None)
	>>> next(id)
	'0000000001'
	>>> next(id)
	'0000000002'

	# add a delimiter
	class MyIdentifier(NumericIdentifier):
    	identifier_pattern = r'^[0-9]{4}\-[0-9]{4}\-[0-9]{4}$'
    	delimeter = '-'
    	seed = ('3200-0000-0000')

	>>> id = MyIdentifier(None)
	>>> next(id)
	'3200-0000-0001'
	>>> next(id)
	'3200-0000-0002'

	# start from the last identifier
	>>> id = MyIdentifier('3200-0000-3227')
	>>> next(id)
	'3200-0000-3228'
	

Alphanumeric Identifiers
------------------------

	from getresults_identifier import AlpanumericIdentifier

	class MyIdentifier(AlpanumericIdentifier):
	    alpha_pattern = r'^[A-Z]{3}$'
    	numeric_pattern = r'^[0-9]{4}$'
    	seed = ('AAA', '0000')
		
With the above your identifier will start with 'AAA0001'. For example:

	>>> from getresults_receive.receive_identifier import ReceiveIdentifier
	>>> new_id = MyIdentifier(None)
	>>> print(new_id)
	'AAA0001'

The identifier increments on the numeric sequence then the alpha:

	>>> id = MyIdentifier('AAZ9998)
	>>> next(id)
	'AAA9999'	

	>>> next(id)
	'AAB9999'	

	>>> id = MyIdentifier('AAZ9998)
	>>> next(id)
	'AAZ9999'	
	>>> next(id)
	'ABA0001'	

See `getresults-receive` for sample usage with `settings` and a `History` model.

Short Identifiers
-----------------

Creates a small identifier that is almost unique, for example, across 25 Edc devices in a community. We use these as sample requisition identifiers that are transcribed manually onto a tube from the Edc screen in a household. Once the sample is received at the local lab it is allocated a laboratory-wide unique specimen identifier.

    from .short_identifier import ShortIdentifier
    
    >>> options = {'prefix': 22}
    >>> id = ShortIdentifier(options=options)
	>>> print(id)
	'22ECY42'
	>>> next(id)
	'228AP77'
	
... add more to the prefix, such as device code and community code.

	from getresults_identifier.short_identifier import ShortIdentifier
	
	
	class RequisitionIdentifier(ShortIdentifier):
	    
		identifier_type = 'requisition'
		prefix_pattern = r'^[0-9]{4}'
		template = '{device_id}{community_id}{random_string}'

		@property
		def options(self):
			if 'prefix' not in self._options:
				self._options.update(
					{'prefix': str(self._options.get('device_id')) + str(self._options.get('community_id'))})
			return self._options

    >>> options = {'device_id': 22, 'community_id': '12'}
    >>> id = RequisitionIdentifier(options=options)
	>>> print(id)
	'2212X9V92'
	>>> next(id)
	'2212PC7E7'

... if you prefer not to use the `IdentifierHistory` model, for example, if you are filling in a model field on save():

	from my_app.models import Requisition

	class RequisitionIdentifier(ShortIdentifier):
	
	    identifier_type = 'requisition'
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
