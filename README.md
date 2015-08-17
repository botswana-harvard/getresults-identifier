[![Build Status](https://travis-ci.org/botswana-harvard/getresults-identifier.svg?branch=develop)](https://travis-ci.org/botswana-harvard/getresults-identifier)
[![Coverage Status](https://coveralls.io/repos/botswana-harvard/getresults-identifier/badge.svg?branch=develop&service=github)](https://coveralls.io/github/botswana-harvard/getresults-identifier?branch=develop)

# getresults-identifier

Base classes for identifiers.

Numeric Identifiers
-------------------

The numeric identifier uses a check-digit and may have a separator if specified.

	from getresults_identifier import NumericIdentifier

	class MyIdentifier(NumericIdentifier):
		pass
		
	>>> id = MyIdentifier(None)
	>>> id
	MyIdentifier('00000000018')
	>>> next(id)
	'00000000026'
	>>> next(id)
	'00000000034'


	# add a separator
	class MyIdentifier(NumericIdentifier):
    	identifier_pattern = r'^[0-9]{4}\-[0-9]{4}\-[0-9]{4}$'
    	checkdigit_pattern = r'^\-[0-9]{1}$'
    	separator = '-'
    	seed = ['3200-0000-0000']

	>>> id = MyIdentifier(None)
	>>> id
	MyIdentifier('3200-0000-0001-1')
	>>> next(id)
	'3200-0000-0002-9'
	>>> next(id)
	'3200-0000-0003-7'

	# start from the last identifier, increment is immediate and automatic
	>>> id = MyIdentifier('3200-0000-3222-0')
	>>> id
	MyIdentifier('3200-0000-3223-8')
	

Alphanumeric Identifiers
------------------------

	from getresults_identifier import AlphanumericIdentifier

	class MyIdentifier(AlphanumericIdentifier):
		alpha_pattern = r'^[A-Z]{3}$'
		numeric_pattern = r'^[0-9]{4}$'
		seed = ['AAA', '0000']
		
	>>> id = MyIdentifier(None)
	>>> id
	MyIdentifier('AAA00015')

Your identifier will starts with 'AAA0001' plus the checkdigit "5". Subsequent calls to next increment like this:

	>>> print(next(id))
	AAA00023
	>>> print(next(id))
	AAA00031
	>>> print(next(id))
	AAA00049


The identifier increments on the numeric sequence then the alpha:

	>>> id = MyIdentifier('AAA99991)
	>>> id
	MyIdentifier('AAB00013')	

	>>> next(id)
	'AAB00021'	
	>>> next(id)
	'AAB00039'	
	>>> next(id)
	'AAB00047'	

	>>> id = MyIdentifier('AAB99999')
	>>> id
	MyIdentifier('AAC00010')
	...	

See `getresults-receive` for sample usage with `settings` and a `History` model.

Short Identifiers
-----------------

Creates a small identifier that is almost unique, for example, across 25 Edc devices in a community. We use these as sample requisition identifiers that are transcribed manually onto a tube from the Edc screen in a household. Once the sample is received at the local lab it is allocated a laboratory-wide unique specimen identifier.

    from getresults_identifier import ShortIdentifier
    
    >>> ShortIdentifier()
    ShortIdentifier('46ZZ2')

Add a static prefix -- prefix(2) + identifier(5):

	from getresults_identifier import ShortIdentifier
	
	class MyIdentifier(ShortIdentifier):
    	prefix_pattern = r'^[0-9]{2}$'
 	
    >>> options = {'prefix': 22}
    >>> id = MyIdentifier(options=options)
	>>> id
	MyIdentifier('22UYMBT')
	>>> next(id)
	'22KM84G'

Add a checkdigit -- prefix(2) + identifier(5) + checkdigit(1):

	from getresults_identifier import ShortIdentifier
	
	class MyIdentifier(ShortIdentifier):
    	prefix_pattern = r'^[0-9]{2}$'
    	checkdigit_pattern = r'^[0-9]{1}$'

    >>> options = {'prefix': 22}
    >>> id = MyIdentifier(options=options)
	>>> id
	MyIdentifier('223GF8A3')
	>>> next(id)
	'22DXVW23'

We use this in edc-quota to get a confirmation code:

	from getresults_identifier import ShortIdentifier
	
	class ConfirmationCode(ShortIdentifier):
	
	    identifier_type = 'confirmation'
	    prefix_pattern = ''

	>>> code = ConfirmationCode()
	>>> print(code)
	CAT33
	>>> next(code)
	3FU7D
	
Add more to the prefix, such as device code and community code.

	from getresults_identifier.short_identifier import ShortIdentifier	
	
	class RequisitionIdentifier(ShortIdentifier):
	    
		identifier_type = 'requisition'
		prefix_pattern = r'^[0-9]{4}$'
		template = '{device_id}{community_id}{random_string}'

		@property
		def options(self):
			if 'prefix' not in self._options:
				self._options.update(
					{'prefix': str(self._options.get('device_id')) + str(self._options.get('community_id'))})
			return self._options

    >>> options = {'device_id': 22, 'community_id': '12'}
    >>> id = RequisitionIdentifier(options=options)
	>>> id
	RequisitionIdentifier('22126MZXD')
	>>> next(id)
	'2212Y899C'

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

			
Batch Identifier
----------------

To have an identifier prefixed by the current date stamp:

	from getresults_identifier.batch_identifier import BatchIdentifier	

	>>> datetime.today().strftime('%Y%m%d)
	20150817
	>>> id = BatchIdentifier()
	>>> id
	BatchIdentifier('201508170001')
	>>> next(id)
	'201508170002'

	
	
	