<?php
include_once('ufo_campaign_item.php');
class ufo_campaign_items {
	// public attributes
	var $uid;
	var $campaign_item = array();
	var $addedObject = 0;

	// private attributes
	var $classname;
	var $initialized;

	// Security
	var $visibility = array(
	'view' => 'public',
	'submit' => 'public',
	'edit' => 'public',
	'add' => 'public'
	);


	function ufo_campaign_items( $argv=0 ) {
		global $ufoSession;

		// hopefully this isn't necessary.
		$this->className = "campaign_items";
		$this->initialize($argv);
	}
	function initialize($argv) {
		// Find the member data.
		global $ufoDb;
		global $ufoSession;
		global $Log;

		if (isset($argv['uid'])) {
			$this->uid = $argv['uid'];
		} else {
			$this->uid = $ufoSession->userId();
		}
		$link = $ufoDb->getLink();

 		$query = "SELECT * from ufo_campaign_item where uid=$this->uid";
		$result = pg_query($query) or die("Query failed : " . pg_last_error());

		$idx = 0;
		while ($row = pg_fetch_assoc($result) ) {
			$to =& new ufo_campaign_item(0);
			$to->initRow( $row );
			$this->campaign_item[] =& $to;
			$idx += 1;
		}

		 /* Free resultset */
		
	}
	function link() {
		global $ufoGlobals;
		global $page;
		if ( !strcmp($page, 'profile') ) {
			$c = "<a href=\"http://{$ufoGlobals->domain}/{$ufoGlobals->rootdir}/main.php?page=profile&obj=profile&method=select&ufo[facet]=campaign_items\">campaign_items</a>";
		} else {
			$c = "<a href=\"http://{$ufoGlobals->domain}/{$ufoGlobals->rootdir}/main.php?page=campaign_items\">campaign_items</a>";
		}
		return $c;
	}
	function add() {
		// check if we have quota.
		if (True) {

			// create an empty campaign_item.
			$o =& new ufo_campaign_item(0);
			$this->addedObject =& $o;
		
			// create an entry in the db.
			$o->initialize();
			$o->create();
			$o->edit();

			// add it to the campaign_item array.
			$this->campaign_item[] = $o;
		}
	}
	function view_campaign_item() {
		$c = "";

		$c .= "<br><h3>campaign_items:</h3>";

		$c .= "
		<table class=\"stats\" border>
		";
		$lfirst = True;
		foreach ( $this->campaign_item as $r ) {
			if ( $lfirst ) {
				$table_headers = $r->table_headers();
				$c .= "
			<tr>
			{$table_headers}
			</tr>
				";
				$lfirst = False;
			}
			$c .= "<tr>";
			$c .= $r->viewAsTableRow();
			$c .= "</tr>";
		}
		if ( $lfirst ) {
			$table_headers = "No campaign_item listed currently";
			$c .= "
			<tr>
			{$table_headers}
			</tr>
			";
			$lfirst = False;
		}
		$c .= "</table>";
		return $c;
		
	}
	function view() {
		$c = "";

		if ( $this->addedObject ) {
			$c .= $this->addedObject->view();
			return $c;
		}

		$c .= "<div id=\"campaign_items\">";
		$c .= $this->view_campaign_item();

		// If we have quota
		$c .= "<br>";
		if (True) {
		$c .= "
		<form action=\"main.php?page=campaign_items&obj=campaign_items&method=add\" method=\"post\">
		<input type=\"submit\" name=\"submit\" value=\"Add Entry\">
		</form>
		";

		}
		$c .= "</div>";
		return $c;
	}
}
?>
