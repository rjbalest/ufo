<?php
include_once('ufo_campaign_base.php');

class ufo_campaign extends ufo_campaign_base {

	// user attributes

	// Security
	var $visibility = array(
	'view' => 'public',
	'submit' => 'public',
	'edit' => 'public',
	'add' => 'public'
	);


	function ufo_campaign( $argv=-1 ) {
		global $ufoDb;
		global $ufoSession;
		$this->readOnly = 1;
		// hopefully this isn't necessary.
		$this->className = "campaign";
		$this->link_edit = "main.php?obj=campaign&ufo[oid]={\$this->oid}&method=edit&page={\$page}";
		$this->link_submit = "main.php?obj=campaign&method=submit&page=\$page";

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
	function validate( $ufo ) {
		
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
		$LFACET = FALSE;
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
