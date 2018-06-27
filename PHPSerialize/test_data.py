data = {
	True		: 'Yes',
	False		: 'No',
	None		: 'nullkey',
	'105'		: 'intkey',
	'true'		: True,
	'false'		: False,
	'null'		: None,
	'string'	: "Scott\"Hurring",
	'int'		: 2,
	#'exp'		: 7E-10,
	'double'	: 21.80,
	'tuple'		: (1,2),
	'list'		: [1,2],
	'dict' : {
		'key1' : 'value1',
		'key2' : {
			'key2.1' : 'value2.1',
			22 : 'twotwo',
		},
	},
	# Very large integer
	'massive_int'	: pow(2, 34),
	# Integers
	'negative'	: -20,
	'negfloat'	: -20.4,
}

session = {'a' : 1, 
'b' : 'x|yz',
'data' : data}
