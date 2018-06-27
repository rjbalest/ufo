<?php
class ufo_campaign_item_base {
	// public attributes
	var $oid;
	var $uid;
	var $campaign_id;
	var $product_id;
	var $bid;
	var $status;
	var $destination;
	var $clicks;
	var $impressions;
	var $ctr;
	var $avg_cpc;
	var $cost;
	

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


	function ufo_campaign_item_base( $oid=-1 ) {
		global $ufoDb;
		global $ufoSession;
		$this->readOnly = 1;
		// hopefully this isn't necessary.
		$this->className = "campaign_item";
		$this->link_edit = "main.php?obj=campaign_item&ufo[oid]={\$this->oid}&method=edit&page={\$page}";
		$this->link_submit = "main.php?obj=campaign_item&method=submit&page=\$page";

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
		$this->campaign_id = "None";
		$this->product_id = "None";
		$this->bid = "None";
		$this->status = "None";
		$this->destination = "None";
		$this->clicks = "None";
		$this->impressions = "None";
		$this->ctr = "None";
		$this->avg_cpc = "None";
		$this->cost = "None";
		
	}
	function initRow( $row ) {
		// Initialize through SQL row.
		$this->oid = $row['id'];
		$this->uid = $row['uid'];
		$this->campaign_id = $row['campaign_id'];
		$this->product_id = $row['product_id'];
		$this->bid = $row['bid'];
		$this->status = $row['status'];
		$this->destination = $row['destination'];
		$this->clicks = $row['clicks'];
		$this->impressions = $row['impressions'];
		$this->ctr = $row['ctr'];
		$this->avg_cpc = $row['avg_cpc'];
		$this->cost = $row['cost'];
		
	}
	function create() {
		// create it in the DB
		global $ufoSession;
		global $ufoDb;
		$link = $ufoDb->getLink();
		$this->uid = $ufoSession->userId();

		// insert
		$query = "INSERT INTO ufo_campaign_item (uid, campaign_id, product_id, bid, status, destination, clicks, impressions, ctr, avg_cpc, cost) VALUES ($this->uid, $this->campaign_id, $this->product_id, $this->bid, $this->status, '$this->destination', $this->clicks, $this->impressions, $this->ctr, $this->avg_cpc, $this->cost)";
		$result = pg_query($query) or die("Query failed : " . pg_last_error());
		/* Get the auto increment Id of the last insert. */
		$this->oid = $ufoDb->insert_id("ufo_campaign_item_seq");
		$this->initialized = True;
	}
	function save() {
		global $ufoDb;
		// update it in the DB
		$link = $ufoDb->getLink();
		$oid = $this->oid;
		if ($this->initialized == True) {
			$query = "UPDATE ufo_campaign_item set campaign_id='$this->campaign_id', product_id='$this->product_id', bid='$this->bid', status='$this->status', destination='$this->destination', clicks='$this->clicks', impressions='$this->impressions', ctr='$this->ctr', avg_cpc='$this->avg_cpc', cost='$this->cost' WHERE id=$oid";
			$result = pg_query($query) or die("Query failed : " . pg_last_error());
		} else {
			$this->create();
		}
	}
	function load( $oid ) {
		global $ufoDb;
		$link = $ufoDb->getLink();

		$query = "SELECT uid, campaign_id, product_id, bid, status, destination, clicks, impressions, ctr, avg_cpc, cost FROM ufo_campaign_item WHERE id=$oid";

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
		if (isset($ufo['campaign_id'])) { $this->campaign_id = $ufo['campaign_id']; }
		if (isset($ufo['product_id'])) { $this->product_id = $ufo['product_id']; }
		if (isset($ufo['bid'])) { $this->bid = $ufo['bid']; }
		if (isset($ufo['status'])) { $this->status = $ufo['status']; }
		if (isset($ufo['destination'])) { $this->destination = $ufo['destination']; }
		if (isset($ufo['clicks'])) { $this->clicks = $ufo['clicks']; }
		if (isset($ufo['impressions'])) { $this->impressions = $ufo['impressions']; }
		if (isset($ufo['ctr'])) { $this->ctr = $ufo['ctr']; }
		if (isset($ufo['avg_cpc'])) { $this->avg_cpc = $ufo['avg_cpc']; }
		if (isset($ufo['cost'])) { $this->cost = $ufo['cost']; }
		$this->save();
		$this->readOnly = TRUE;

	}
	function link() {
		global $ufoGlobals;
		$c = "<a href=\"http://{$ufoGlobals->domain}/main.php?page=campaign_item\">campaign_item</a>";
		return $c;
	}
	function table_headers() {
		$c = "";
		$c .= "
		
<th>
campaign_id
</th>
<th>
product_id
</th>
<th>
bid
</th>
<th>
status
</th>
<th>
destination
</th>
<th>
clicks
</th>
<th>
impressions
</th>
<th>
ctr
</th>
<th>
avg_cpc
</th>
<th>
cost
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
		
<td  class=\"labelValue\">$this->campaign_id </td>
<td  class=\"labelValue\">$this->product_id </td>
<td  class=\"labelValue\">$this->bid </td>
<td  class=\"labelValue\">$this->status </td>
<td  class=\"labelValue\">$this->destination </td>
<td  class=\"labelValue\">$this->clicks </td>
<td  class=\"labelValue\">$this->impressions </td>
<td  class=\"labelValue\">$this->ctr </td>
<td  class=\"labelValue\">$this->avg_cpc </td>
<td  class=\"labelValue\">$this->cost </td>
		"; 
		} else {
		  if ($this->initialized == TRUE) {
		$c = "
		
<form action=\"main.php?obj=campaign_item&method=submit&page=$page\" method=\"post\">
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[campaign_id]\" value=\"$this->campaign_id\"></td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[product_id]\" value=\"$this->product_id\"></td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[bid]\" value=\"$this->bid\"></td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[status]\" value=\"$this->status\"></td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[destination]\" value=\"$this->destination\"></td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[clicks]\" value=\"$this->clicks\"></td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[impressions]\" value=\"$this->impressions\"></td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[ctr]\" value=\"$this->ctr\"></td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[avg_cpc]\" value=\"$this->avg_cpc\"></td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[cost]\" value=\"$this->cost\"></td>
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
<td  class=\"label\">campaign_id:</td>
<td  class=\"labelValue\">$this->campaign_id </td>
</tr>
<tr>
<td  class=\"label\">product_id:</td>
<td  class=\"labelValue\">$this->product_id </td>
</tr>
<tr>
<td  class=\"label\">bid:</td>
<td  class=\"labelValue\">$this->bid </td>
</tr>
<tr>
<td  class=\"label\">status:</td>
<td  class=\"labelValue\">$this->status </td>
</tr>
<tr>
<td  class=\"label\">destination:</td>
<td  class=\"labelValue\">$this->destination </td>
</tr>
<tr>
<td  class=\"label\">clicks:</td>
<td  class=\"labelValue\">$this->clicks </td>
</tr>
<tr>
<td  class=\"label\">impressions:</td>
<td  class=\"labelValue\">$this->impressions </td>
</tr>
<tr>
<td  class=\"label\">ctr:</td>
<td  class=\"labelValue\">$this->ctr </td>
</tr>
<tr>
<td  class=\"label\">avg_cpc:</td>
<td  class=\"labelValue\">$this->avg_cpc </td>
</tr>
<tr>
<td  class=\"label\">cost:</td>
<td  class=\"labelValue\">$this->cost </td>
</tr>
</table>
[<a href=\"main.php?obj=campaign_item&ufo[oid]={$this->oid}&method=edit&page={$page}\">edit</a>]
		"; 
		} else {
		  if ($this->initialized == TRUE) {
		$c = "
		
<form action=\"main.php?obj=campaign_item&method=submit&page=$page\" method=\"post\">
<table class=\"stats\" border cellpadding=\"0\" style=\"border-collapse: collapse\" width=\"50%\">
<tr>
<td class=\"label\">campaign_id : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[campaign_id]\" value=\"$this->campaign_id\"></td>
</tr>
<tr>
<td class=\"label\">product_id : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[product_id]\" value=\"$this->product_id\"></td>
</tr>
<tr>
<td class=\"label\">bid : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[bid]\" value=\"$this->bid\"></td>
</tr>
<tr>
<td class=\"label\">status : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[status]\" value=\"$this->status\"></td>
</tr>
<tr>
<td class=\"label\">destination : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[destination]\" value=\"$this->destination\"></td>
</tr>
<tr>
<td class=\"label\">clicks : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[clicks]\" value=\"$this->clicks\"></td>
</tr>
<tr>
<td class=\"label\">impressions : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[impressions]\" value=\"$this->impressions\"></td>
</tr>
<tr>
<td class=\"label\">ctr : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[ctr]\" value=\"$this->ctr\"></td>
</tr>
<tr>
<td class=\"label\">avg_cpc : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[avg_cpc]\" value=\"$this->avg_cpc\"></td>
</tr>
<tr>
<td class=\"label\">cost : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[cost]\" value=\"$this->cost\"></td>
</tr>
</table>
<input type=\"hidden\" name=\"ufo[oid]\" value=\"$this->oid\">
<input type=\"hidden\" name=\"method\" value=\"submit\">
<input type=\"submit\" name=\"submit\" value=\"submit\">
</form>
		";
		  } else {
		$c = "
		
<form action=\"main.php?obj=campaign_item&method=submit&page=$page\" method=\"post\">
<table class=\"stats\" border cellpadding=\"0\" style=\"border-collapse: collapse\" width=\"50%\">
<tr>
<td class=\"label\">campaign_id : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[campaign_id]\" value=\"$this->campaign_id\"></td>
</tr>
<tr>
<td class=\"label\">product_id : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[product_id]\" value=\"$this->product_id\"></td>
</tr>
<tr>
<td class=\"label\">bid : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[bid]\" value=\"$this->bid\"></td>
</tr>
<tr>
<td class=\"label\">status : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[status]\" value=\"$this->status\"></td>
</tr>
<tr>
<td class=\"label\">destination : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[destination]\" value=\"$this->destination\"></td>
</tr>
<tr>
<td class=\"label\">clicks : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[clicks]\" value=\"$this->clicks\"></td>
</tr>
<tr>
<td class=\"label\">impressions : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[impressions]\" value=\"$this->impressions\"></td>
</tr>
<tr>
<td class=\"label\">ctr : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[ctr]\" value=\"$this->ctr\"></td>
</tr>
<tr>
<td class=\"label\">avg_cpc : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[avg_cpc]\" value=\"$this->avg_cpc\"></td>
</tr>
<tr>
<td class=\"label\">cost : </td>
<td class=\"labelValue\"><input type=\"text\" name=\"ufo[cost]\" value=\"$this->cost\"></td>
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
