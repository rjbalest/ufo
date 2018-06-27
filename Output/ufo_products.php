<?php
include_once('ufo_product.php');
class ufo_products {
	// public attributes
	var $uid;
	var $product = array();
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


	function ufo_products( $argv=0 ) {
		global $ufoSession;

		// hopefully this isn't necessary.
		$this->className = "products";
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

 		$query = "SELECT * from ufo_product where uid=$this->uid";
		$result = pg_query($query) or die("Query failed : " . pg_last_error());

		$idx = 0;
		while ($row = pg_fetch_assoc($result) ) {
			$to =& new ufo_product(0);
			$to->initRow( $row );
			$this->product[] =& $to;
			$idx += 1;
		}

		 /* Free resultset */
		
	}
	function link() {
		global $ufoGlobals;
		global $page;
		if ( !strcmp($page, 'profile') ) {
			$c = "<a href=\"http://{$ufoGlobals->domain}/{$ufoGlobals->rootdir}/main.php?page=profile&obj=profile&method=select&ufo[facet]=products\">products</a>";
		} else {
			$c = "<a href=\"http://{$ufoGlobals->domain}/{$ufoGlobals->rootdir}/main.php?page=products\">products</a>";
		}
		return $c;
	}
	function add() {
		// check if we have quota.
		if (True) {

			// create an empty product.
			$o =& new ufo_product(0);
			$this->addedObject =& $o;
		
			// create an entry in the db.
			$o->initialize();
			$o->create();
			$o->edit();

			// add it to the product array.
			$this->product[] = $o;
		}
	}
	function view_product() {
		$c = "";

		$c .= "<br><h3>products:</h3>";

		$c .= "
		<table class=\"stats\" border>
		";
		$lfirst = True;
		foreach ( $this->product as $r ) {
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
			$table_headers = "No product listed currently";
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

		$c .= "<div id=\"products\">";
		$c .= $this->view_product();

		// If we have quota
		$c .= "<br>";
		if (True) {
		$c .= "
		<form action=\"main.php?page=products&obj=products&method=add\" method=\"post\">
		<input type=\"submit\" name=\"submit\" value=\"Add Entry\">
		</form>
		";

		}
		$c .= "</div>";
		return $c;
	}
}
?>
