#!/usr/bin/php
<?
# Decode session_encode output from STDIN

$h = join("", file('/dev/stdin'));
@session_start();
session_decode(rtrim($h));
print_r($_SESSION);

?>
