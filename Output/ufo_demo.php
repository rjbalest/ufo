<?php
class ufo_demo {
	// public attributes
	var $oid;
	var $uid;
	var $address;
	var $email;
	var $phone;
	var $url;
	

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


	function ufo_demo( $oid=-1 ) {
		global $ufoDb;
		global $ufoSession;
		$this->readOnly = 1;
		// hopefully this isn't necessary.
		$this->className = "demo";
		$this->link_edit = "main.php?obj=demo&ufo[oid]={\$this->oid}&method=edit&page={\$page}";
		$this->link_submit = "main.php?obj=demo&method=submit&page=\$page";

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
			$this->selected[$facet] = True;
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
		$this->address = "";
		$this->email = "";
		$this->phone = "";
		$this->url = "";
		
	}
	function initRow( $row ) {
		// Initialize through SQL row.
		$this->oid = $row['id'];
		$this->uid = $row['uid'];
		$this->address = $row['address'];
		$this->email = $row['email'];
		$this->phone = $row['phone'];
		$this->url = $row['url'];
		
	}
	function create() {
		// create it in the DB
		global $ufoSession;
		global $ufoDb;
		$link = $ufoDb->getLink();
		$this->uid = $ufoSession->userId();

		// insert
		$query = INSERT INTO ufo_demo (uid, address, email, phone, url) VALUES ('$this->uid', '$this->address', '$this->email', '$this->phone', '$this->url');
		$result = mysql_query($query) or die("Query failed : " . mysql_error());
		/* Get the auto increment Id of the last insert. */
		$this->oid = mysql_insert_id($link);
		$this->initialized = True;
	}
	function save() {
		global $ufoDb;
		// update it in the DB
		$link = $ufoDb->getLink();
		$oid = $this->oid;
		if ($this->initialized == True) {
			$query = "UPDATE ufo_demo set address='$this->address', email='$this->email', phone='$this->phone', url='$this->url' WHERE id=$oid";
			$result = mysql_query($query) or die("Query failed : " . mysql_error());
		} else {
			$this->create();
		}
	}
	function load( $oid ) {
		global $ufoDb;
		$link = $ufoDb->getLink();

		$query = "SELECT uid, address, email, phone, url FROM ufo_demo WHERE id=$oid";

		$result = mysql_query($query) or die("Query failed : " . mysql_error());
		$row = mysql_fetch_array($result, MYSQL_ASSOC);
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
		if (isset($ufo[address])) { $this->address = $ufo[address]; }
		if (isset($ufo[email])) { $this->email = $ufo[email]; }
		if (isset($ufo[phone])) { $this->phone = $ufo[phone]; }
		if (isset($ufo[url])) { $this->url = $ufo[url]; }
		$this->save();
		$this->readOnly = TRUE;

	}
	function link() {
		global $ufoGlobals;
		$c = "<a href=\"http://{$ufoGlobals->domain}/main.php?page=demo\">demo</a>";
		return $c;
	}
	function table_headers() {
		$c = "";
		$c .= "
		
<th>
address
</th>
<th>
email
</th>
<th>
phone
</th>
<th>
url
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
		
<td  class=\"labelValue\">$this->address </td>
<td  class=\"labelValue\">$this->email </td>
<td  class=\"labelValue\">$this->phone </td>
<td  class=\"labelValue\">$this->url </td>
		"; 
		} else {
		  if ($this->initialized == TRUE) {
		$c = "
		
<form action=\"main.php?obj=demo&method=submit&page=$page\" method=\"post\">
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[address]\" value=\"$this->address\"></td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[email]\" value=\"$this->email\"></td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[phone]\" value=\"$this->phone\"></td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[url]\" value=\"$this->url\"></td>
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
<td  class=\"label\">address:</td>
<td  class=\"labelValue\">$this->address </td>
</tr>
<tr>
<td  class=\"label\">email:</td>
<td  class=\"labelValue\">$this->email </td>
</tr>
<tr>
<td  class=\"label\">phone:</td>
<td  class=\"labelValue\">$this->phone </td>
</tr>
<tr>
<td  class=\"label\">url:</td>
<td  class=\"labelValue\">$this->url </td>
</tr>
</table>
[<a href=\"main.php?obj=demo&ufo[oid]={$this->oid}&method=edit&page={$page}\">edit</a>]
		"; 
		} else {
		  if ($this->initialized == TRUE) {
		$c = "
		
<form action=\"main.php?obj=demo&method=submit&page=$page\" method=\"post\">
<table class=\"stats\" border cellpadding=\"0\" style=\"border-collapse: collapse\" width=\"50%\">
<tr>
<td class=\"label\">address : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[address]\" value=\"$this->address\"></td>
</tr>
<tr>
<td class=\"label\">email : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[email]\" value=\"$this->email\"></td>
</tr>
<tr>
<td class=\"label\">phone : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[phone]\" value=\"$this->phone\"></td>
</tr>
<tr>
<td class=\"label\">url : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[url]\" value=\"$this->url\"></td>
</tr>
</table>
<input type=\"hidden\" name=\"ufo[oid]\" value=\"$this->oid\">
<input type=\"hidden\" name=\"method\" value=\"submit\">
<input type=\"submit\" name=\"submit\" value=\"submit\">
</form>
		";
		  } else {
		$c = "
		
<form action=\"main.php?obj=demo&method=submit&page=$page\" method=\"post\">
<table class=\"stats\" border cellpadding=\"0\" style=\"border-collapse: collapse\" width=\"50%\">
<tr>
<td class=\"label\">address : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[address]\" value=\"$this->address\"></td>
</tr>
<tr>
<td class=\"label\">email : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[email]\" value=\"$this->email\"></td>
</tr>
<tr>
<td class=\"label\">phone : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[phone]\" value=\"$this->phone\"></td>
</tr>
<tr>
<td class=\"label\">url : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[url]\" value=\"$this->url\"></td>
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
