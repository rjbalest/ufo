#!/usr/bin/php
<?
# Unserialize serialized data from STDIN

$h = join("", file('/dev/stdin'));
print_r(unserialize(rtrim($h)));

?>