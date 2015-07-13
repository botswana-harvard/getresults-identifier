# getresults-identifier
Base classes for identifiers



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
