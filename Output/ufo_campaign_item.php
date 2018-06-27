<?php
include_once('ufo_campaign_item_base.php');

class ufo_campaign_item extends ufo_campaign_item_base {

	// user attributes

	// Security
	var $visibility = array(
	'view' => 'public',
	'submit' => 'public',
	'edit' => 'public',
	'add' => 'public'
	);


	function ufo_campaign_item( $argv=-1 ) {
		global $ufoDb;
		global $ufoSession;
		$this->readOnly = 1;
		// hopefully this isn't necessary.
		$this->className = "campaign_item";
		$this->link_edit = "main.php?obj=campaign_item&ufo[oid]={\$this->oid}&method=edit&page={\$page}";
		$this->link_submit = "main.php?obj=campaign_item&method=submit&page=\$page";

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
	function validate( $ufo ) {
		
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
		$LFACET = FALSE;
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
