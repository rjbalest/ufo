<html>
<body>
<?php
$sel = $_REQUEST['sel']?$_REQUEST['sel']:"last_posted, title";
$q = stripslashes($_REQUEST['q']?$_REQUEST['q']:"country_id=3 and 'for sale'");
$lim = $_REQUEST['lim']?$_REQUEST['lim']:"10";
?>
<pre>
<form action="index.php">
select <input name="sel", value="<?php echo $sel; ?>"/> where <input name="q" size="50" value="<?php echo $q; ?>"/> order by last_posted desc limit <input name="lim" value="<?php echo $lim; ?>"/>
<input type="submit" value=" Search "/>
</form>

<?php 
include("PHPRPC.php"); 
$client = new PHPRPC_Client('69.9.38.21', 8007);
var_dump($client->query('query', implode("", array("select ", $sel, " where ", $q, " order by last_posted desc limit ", $lim))));
?>
</pre>
</body>
</html>