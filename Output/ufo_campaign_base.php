<?php
class ufo_campaign_base {
	// public attributes
	var $oid;
	var $uid;
	var $status;
	var $clicks;
	var $impressions;
	var $ctr;
	var $avg_cpc;
	var $cost;
	var $name;
	var $description;
	var $budget;
	

	// facets - subviews
	var $facets = array(
	'rename','items');

	// selectors 
	var $selected = array(
	'rename' => False
	,'items' => False
	);

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


	function ufo_campaign_base( $oid=-1 ) {
		global $ufoDb;
		global $ufoSession;
		$this->readOnly = 1;
		// hopefully this isn't necessary.
		$this->className = "campaign";
		$this->link_edit = "main.php?obj=campaign&ufo[oid]={\$this->oid}&method=edit&page={\$page}";
		$this->link_submit = "main.php?obj=campaign&method=submit&page=\$page";

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
		$this->status = "0";
		$this->clicks = "0";
		$this->impressions = "0";
		$this->ctr = "0";
		$this->avg_cpc = "0.0";
		$this->cost = "0.0";
		$this->name = "None";
		$this->description = "Unknown";
		$this->budget = "0.0";
		
	}
	function initRow( $row ) {
		// Initialize through SQL row.
		$this->oid = $row['id'];
		$this->uid = $row['uid'];
		$this->status = $row['status'];
		$this->clicks = $row['clicks'];
		$this->impressions = $row['impressions'];
		$this->ctr = $row['ctr'];
		$this->avg_cpc = $row['avg_cpc'];
		$this->cost = $row['cost'];
		$this->name = $row['name'];
		$this->description = $row['description'];
		$this->budget = $row['budget'];
		
	}
	function create() {
		// create it in the DB
		global $ufoSession;
		global $ufoDb;
		$link = $ufoDb->getLink();
		$this->uid = $ufoSession->userId();

		// insert
		$query = "INSERT INTO ufo_campaign (uid, status, clicks, impressions, ctr, avg_cpc, cost, name, description, budget) VALUES ($this->uid, $this->status, $this->clicks, $this->impressions, $this->ctr, $this->avg_cpc, $this->cost, '$this->name', '$this->description', $this->budget)";
		$result = pg_query($query) or die("Query failed : " . pg_last_error());
		/* Get the auto increment Id of the last insert. */
		$this->oid = $ufoDb->insert_id("ufo_campaign_seq");
		$this->initialized = True;
	}
	function save() {
		global $ufoDb;
		// update it in the DB
		$link = $ufoDb->getLink();
		$oid = $this->oid;
		if ($this->initialized == True) {
			$query = "UPDATE ufo_campaign set status='$this->status', clicks='$this->clicks', impressions='$this->impressions', ctr='$this->ctr', avg_cpc='$this->avg_cpc', cost='$this->cost', name='$this->name', description='$this->description', budget='$this->budget' WHERE id=$oid";
			$result = pg_query($query) or die("Query failed : " . pg_last_error());
		} else {
			$this->create();
		}
	}
	function load( $oid ) {
		global $ufoDb;
		$link = $ufoDb->getLink();

		$query = "SELECT uid, status, clicks, impressions, ctr, avg_cpc, cost, name, description, budget FROM ufo_campaign WHERE id=$oid";

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
		if (isset($ufo['status'])) { $this->status = $ufo['status']; }
		if (isset($ufo['clicks'])) { $this->clicks = $ufo['clicks']; }
		if (isset($ufo['impressions'])) { $this->impressions = $ufo['impressions']; }
		if (isset($ufo['ctr'])) { $this->ctr = $ufo['ctr']; }
		if (isset($ufo['avg_cpc'])) { $this->avg_cpc = $ufo['avg_cpc']; }
		if (isset($ufo['cost'])) { $this->cost = $ufo['cost']; }
		if (isset($ufo['name'])) { $this->name = $ufo['name']; }
		if (isset($ufo['description'])) { $this->description = $ufo['description']; }
		if (isset($ufo['budget'])) { $this->budget = $ufo['budget']; }
		$this->save();
		$this->readOnly = TRUE;

	}
	function link() {
		global $ufoGlobals;
		$c = "<a href=\"http://{$ufoGlobals->domain}/main.php?page=campaign\">campaign</a>";
		return $c;
	}
	function table_headers() {
		$c = "";
		$c .= "
		
<th>
Status
</th>
<th>
Clicks
</th>
<th>
Impressions
</th>
<th>
Ctr
</th>
<th>
AvgCPC
</th>
<th>
Cost
</th>
<th>
Name
</th>
<th>
Description
</th>
<th>
Budget
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
		
<td  class=\"labelValue\">$this->status </td>
<td  class=\"labelValue\">$this->clicks </td>
<td  class=\"labelValue\">$this->impressions </td>
<td  class=\"labelValue\">$this->ctr </td>
<td  class=\"labelValue\">$this->avg_cpc </td>
<td  class=\"labelValue\">$this->cost </td>
<td  class=\"labelValue\">$this->name </td>
<td  class=\"labelValue\">$this->description </td>
<td  class=\"labelValue\">$this->budget </td>
		"; 
		} else {
		  if ($this->initialized == TRUE) {
		$c = "
		
<form action=\"main.php?obj=campaign&method=submit&page=$page\" method=\"post\"><tr><td>rename</td>";
if ($this->selected['rename']) {
$c .= "

<td class=\"labelValue\"><input type=\"text\" name=\"ufo[name]\" value=\"$this->name\"></td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[description]\" value=\"$this->description\"></td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[budget]\" value=\"$this->budget\"></td></tr>";
}
 $c .= "
<tr><td>items</td>";
if ($this->selected['items']) {
$c .= "
</tr>";
}
 $c .= "

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
<td  class=\"label\">Status:</td>
<td  class=\"labelValue\">$this->status </td>
</tr>
<tr>
<td  class=\"label\">Clicks:</td>
<td  class=\"labelValue\">$this->clicks </td>
</tr>
<tr>
<td  class=\"label\">Impressions:</td>
<td  class=\"labelValue\">$this->impressions </td>
</tr>
<tr>
<td  class=\"label\">Ctr:</td>
<td  class=\"labelValue\">$this->ctr </td>
</tr>
<tr>
<td  class=\"label\">AvgCPC:</td>
<td  class=\"labelValue\">$this->avg_cpc </td>
</tr>
<tr>
<td  class=\"label\">Cost:</td>
<td  class=\"labelValue\">$this->cost </td>
</tr>
<tr>
<td  class=\"label\">Name:</td>
<td  class=\"labelValue\">$this->name </td>
</tr>
<tr>
<td  class=\"label\">Description:</td>
<td  class=\"labelValue\">$this->description </td>
</tr>
<tr>
<td  class=\"label\">Budget:</td>
<td  class=\"labelValue\">$this->budget </td>
</tr>
</table>
[<a href=\"main.php?obj=campaign&ufo[oid]={$this->oid}&method=edit&page={$page}\">edit</a>]
		"; 
		} else {
		  if ($this->initialized == TRUE) {
		$c = "
		
<form action=\"main.php?obj=campaign&method=submit&page=$page\" method=\"post\">
<table class=\"stats\" border cellpadding=\"0\" style=\"border-collapse: collapse\" width=\"50%\">";
if ($this->selected['rename']) {$LFACET=TRUE;

$c .= "

<tr>
<td class=\"label\">Name : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[name]\" value=\"$this->name\"></td>
</tr>
<tr>
<td class=\"label\">Description : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[description]\" value=\"$this->description\"></td>
</tr>
<tr>
<td class=\"label\">Budget : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[budget]\" value=\"$this->budget\"></td>
</tr>";
}
 $c .= "
";
if ($this->selected['items']) {$LFACET=TRUE;

$c .= "
";
}
 $c .= "
";
if ( ! $LFACET ) {
$c .= "

<tr>
<td class=\"label\">Status : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[status]\" value=\"$this->status\"></td>
</tr>
<tr>
<td class=\"label\">Clicks : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[clicks]\" value=\"$this->clicks\"></td>
</tr>
<tr>
<td class=\"label\">Impressions : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[impressions]\" value=\"$this->impressions\"></td>
</tr>
<tr>
<td class=\"label\">Ctr : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[ctr]\" value=\"$this->ctr\"></td>
</tr>
<tr>
<td class=\"label\">AvgCPC : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[avg_cpc]\" value=\"$this->avg_cpc\"></td>
</tr>
<tr>
<td class=\"label\">Cost : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[cost]\" value=\"$this->cost\"></td>
</tr>
<tr>
<td class=\"label\">Name : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[name]\" value=\"$this->name\"></td>
</tr>
<tr>
<td class=\"label\">Description : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[description]\" value=\"$this->description\"></td>
</tr>
<tr>
<td class=\"label\">Budget : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[budget]\" value=\"$this->budget\"></td>
</tr>";
}
 $c .= "

</table>
<input type=\"hidden\" name=\"ufo[oid]\" value=\"$this->oid\">
<input type=\"hidden\" name=\"method\" value=\"submit\">
<input type=\"submit\" name=\"submit\" value=\"submit\">
</form>
		";
		  } else {
		$c = "
		
<form action=\"main.php?obj=campaign&method=submit&page=$page\" method=\"post\">
<table class=\"stats\" border cellpadding=\"0\" style=\"border-collapse: collapse\" width=\"50%\">
<tr>
<td class=\"label\">Status : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[status]\" value=\"$this->status\"></td>
</tr>
<tr>
<td class=\"label\">Clicks : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[clicks]\" value=\"$this->clicks\"></td>
</tr>
<tr>
<td class=\"label\">Impressions : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[impressions]\" value=\"$this->impressions\"></td>
</tr>
<tr>
<td class=\"label\">Ctr : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[ctr]\" value=\"$this->ctr\"></td>
</tr>
<tr>
<td class=\"label\">AvgCPC : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[avg_cpc]\" value=\"$this->avg_cpc\"></td>
</tr>
<tr>
<td class=\"label\">Cost : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[cost]\" value=\"$this->cost\"></td>
</tr>
<tr>
<td class=\"label\">Name : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[name]\" value=\"$this->name\"></td>
</tr>
<tr>
<td class=\"label\">Description : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[description]\" value=\"$this->description\"></td>
</tr>
<tr>
<td class=\"label\">Budget : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[budget]\" value=\"$this->budget\"></td>
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
