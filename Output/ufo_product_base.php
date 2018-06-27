<?php
class ufo_product_base {
	// public attributes
	var $oid;
	var $uid;
	var $name;
	var $description;
	

	// facets - subviews
	

	// selectors 
	var $selected = False;

	// private attributes
	var $readOnly;
	var $initialized;
	var $edit_link;
	var $submit_link;
	var $classname;

	// Security
	var $visibility = array(
	'view' => 'public',
	'submit' => 'public',
	'edit' => 'public',
	'add' => 'public'
	);


	function ufo_product_base( $oid=-1 ) {
		global $ufoDb;
		global $ufoSession;
		$this->readOnly = 1;
		// hopefully this isn't necessary.
		$this->className = "product";
		$this->link_edit = "main.php?obj=product&ufo[oid]={\$this->oid}&method=edit&page={\$page}";
		$this->link_submit = "main.php?obj=product&method=submit&page=\$page";

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
	
	
	function SELECT($argv) {
		$c = "";
		if ( isset($argv['facet']) ) {
			$facet = $argv['facet'];
			$this->selected[$facet] = TRUE;
		} 
	}
			
	function edit() {
		$this->setReadWrite();
	}
	function setReadOnly() { $this->readOnly = TRUE; }
	function setReadWrite() { 
		//global $Log;
		$this->readOnly = 0; 
		//$Log->append("In ufo::setReadWrite()");
	}
	function getReadState() {
		//global $Log;
		//$Log->append("In ufo::getReadState($this->readOnly)");
		return $this->readOnly;
	}
	function initialize() {
		$this->name = "None";
		$this->description = "None";
		
	}
	function initRow( $row ) {
		// Initialize through SQL row.
		$this->oid = $row['id'];
		$this->uid = $row['uid'];
		$this->name = $row['name'];
		$this->description = $row['description'];
		
	}
	function create() {
		// create it in the DB
		global $ufoSession;
		global $ufoDb;
		$link = $ufoDb->getLink();
		$this->uid = $ufoSession->userId();

		// insert
		$query = "INSERT INTO ufo_product (uid, name, description) VALUES ($this->uid, '$this->name', '$this->description')";
		$result = pg_query($query) or die("Query failed : " . pg_last_error());
		/* Get the auto increment Id of the last insert. */
		$this->oid = $ufoDb->insert_id("ufo_product_seq");
		$this->initialized = True;
	}
	function save() {
		global $ufoDb;
		// update it in the DB
		$link = $ufoDb->getLink();
		$oid = $this->oid;
		if ($this->initialized == True) {
			$query = "UPDATE ufo_product set name='$this->name', description='$this->description' WHERE id=$oid";
			$result = pg_query($query) or die("Query failed : " . pg_last_error());
		} else {
			$this->create();
		}
	}
	function load( $oid ) {
		global $ufoDb;
		$link = $ufoDb->getLink();

		$query = "SELECT uid, name, description FROM ufo_product WHERE id=$oid";

		$result = pg_query($query) or die("Query failed : " . pg_last_error());
		$row = pg_fetch_assoc($result);
		if (! $row ) {
			// ok if foreign key
			$this->initialized = False;

		} else {
			$this->initRow( $row );
			$this->initialized = True;
			$this->oid = $oid;
		}
		return $this;
	}
	function validate( $ufo ) {
		
	}
	function submit( $ufo ) {
		// update state
		// assert the oid is correct.
		if (isset($ufo['name'])) { $this->name = $ufo['name']; }
		if (isset($ufo['description'])) { $this->description = $ufo['description']; }
		$this->save();
		$this->readOnly = TRUE;

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
