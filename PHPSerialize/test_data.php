<?php
/*
Test data
Should be identical to python 'test_data'
*/
$data = array(
	true		=> 'Yes',
	false		=> 'No',
	NULL		=> 'nullkey',
	'105'		=> 'intkey',
	'true'		=> True,
	'false'		=> False,
	'null'		=> NULL,
	'string'	=> "Scott\"Hurring",
	'int'		=> 2,
	#'exp'		=> 7E-10,
	'double'	=> 21.80,
	'tuple'		=> array(1,2),
	'list'		=> array(1,2),
	'dict' => array(
		'key1' => 'value1',
		'key2' => array(
			'key2.1' => 'value2.1',
			22 => 'twotwo',
		),
	),
	# Very large integer
	'massive_int'	=> pow(2, 34),
	# Integers
	'negative'	=> -20,
	'negfloat'	=> -20.4,
);

@session_start();
$_SESSION = array(
'a' => 1,
'b' => 'x|yz',
'data' => $data);

// Invalid to have '|' in keyname
//'t|est' => 'test',

?>
