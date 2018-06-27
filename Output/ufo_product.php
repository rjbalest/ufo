<?php
include_once('ufo_product_base.php');

class ufo_product extends ufo_product_base {

	// user attributes

	// Security
	var $visibility = array(
	'view' => 'public',
	'submit' => 'public',
	'edit' => 'public',
	'add' => 'public'
	);


	function ufo_product( $argv=-1 ) {
		global $ufoDb;
		global $ufoSession;
		$this->readOnly = 1;
		// hopefully this isn't necessary.
		$this->className = "product";
		$this->link_edit = "main.php?obj=product&ufo[oid]={\$this->oid}&method=edit&page={\$page}";
		$this->link_submit = "main.php?obj=product&method=submit&page=\$page";

		// Handle mixed args, possibly an array.
		if ( is_array($argv) ) {
			if ( isset($argv['oid']) ) {
				$oid = $argv['oid'];
			} else {
				$oid = -1;
			}
		} else {
			$oid = $argv;
		}

		if ( $oid != -1 ) {
			// load it
			if ( $oid == 0 ) {
				// return empty
				$this->initialized = False;
			} else {
				$this->load( $oid );
			} 
		}		
	}
	// not generated currently
	function setEditLink( $url ) {
		$this->link_edit = $url;
	}
	function setSubmitLink( $url ) {
		$this->link_submit = $url;
	}
	function initialize() {
		$this->name = "None";
		$this->description = "None";
		
	}
	function validate( $ufo ) {
		
	}
	function link() {
		global $ufoGlobals;
		$c = "<a href=\"http://{$ufoGlobals->domain}/main.php?page=product\">product</a>";
		return $c;
	}
	function table_headers() {
		$c = "";
		$c .= "
		
<th>
name
</th>
<th>
description
</th>
		";
		return $c;
	}
	function viewAsTableRow() {
		global $ufoGlobals;
		global $page;
		global $CHECKED;
		global $BOOLSTR;
		$c = "";
		if ($this->readOnly == TRUE) {
		$c = "
		
<td  class=\"labelValue\">$this->name </td>
<td  class=\"labelValue\">$this->description </td>
		"; 
		} else {
		  if ($this->initialized == TRUE) {
		$c = "
		
<form action=\"main.php?obj=product&method=submit&page=$page\" method=\"post\">
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[name]\" value=\"$this->name\"></td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[description]\" value=\"$this->description\"></td>
<input type=\"hidden\" name=\"ufo[oid]\" value=\"$this->oid\">
<input type=\"hidden\" name=\"method\" value=\"submit\">
<input type=\"submit\" name=\"submit\" value=\"submit\">
</form>
		";
		  } else {
		$c = "
		
		";
		  }
		}
		return $c;
	}

	function view() {
		global $ufoGlobals;
		global $page;
		global $CHECKED;
		global $BOOLSTR;
		$LFACET = FALSE;
		$c = "";
		if ($this->readOnly == TRUE) {
		$c = "
		
<table class=\"stats\" border cellpadding=\"0\" style=\"border-collapse: collapse\" width=\"50%\">
<tr>
<td  class=\"label\">name:</td>
<td  class=\"labelValue\">$this->name </td>
</tr>
<tr>
<td  class=\"label\">description:</td>
<td  class=\"labelValue\">$this->description </td>
</tr>
</table>
[<a href=\"main.php?obj=product&ufo[oid]={$this->oid}&method=edit&page={$page}\">edit</a>]
		"; 
		} else {
		  if ($this->initialized == TRUE) {
		$c = "
		
<form action=\"main.php?obj=product&method=submit&page=$page\" method=\"post\">
<table class=\"stats\" border cellpadding=\"0\" style=\"border-collapse: collapse\" width=\"50%\">
<tr>
<td class=\"label\">name : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[name]\" value=\"$this->name\"></td>
</tr>
<tr>
<td class=\"label\">description : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[description]\" value=\"$this->description\"></td>
</tr>
</table>
<input type=\"hidden\" name=\"ufo[oid]\" value=\"$this->oid\">
<input type=\"hidden\" name=\"method\" value=\"submit\">
<input type=\"submit\" name=\"submit\" value=\"submit\">
</form>
		";
		  } else {
		$c = "
		
<form action=\"main.php?obj=product&method=submit&page=$page\" method=\"post\">
<table class=\"stats\" border cellpadding=\"0\" style=\"border-collapse: collapse\" width=\"50%\">
<tr>
<td class=\"label\">name : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[name]\" value=\"$this->name\"></td>
</tr>
<tr>
<td class=\"label\">description : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[description]\" value=\"$this->description\"></td>
</tr>
</table>
<input type=\"hidden\" name=\"ufo[oid]\" value=\"$this->oid\">
<input type=\"hidden\" name=\"method\" value=\"submit\">
<input type=\"submit\" name=\"submit\" value=\"submit\">
</form>
		";
		  }
		}
		return $c;
	}

}
?>
