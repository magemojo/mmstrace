<?php

//$table=$_GET["table"];
$table = "catalog_product_website";

// strip everything except letters and numbers
$table = preg_replace('/[^a-zA-Z0-9]/', '', $table);

$file = 'query_info';
$searchfor = $table;

// the following line prevents the browser from parsing this as HTML.
header('Content-Type: text/plain');

// get the file contents, assuming the file to be readable (and exist)
$contents = file_get_contents($file);
// escape special characters in the query
$pattern = preg_quote($searchfor, '/');
// finalise the regular expression, matching the whole line
$pattern = "/^.*$pattern.*\$/m";
// search, and store all matching occurences in $matches
if(preg_match_all($pattern, $contents, $matches)){
   echo "Found matches:\n";
   echo implode("\n", $matches[0]);
}
else{
   echo "No matches found";
}

?>
