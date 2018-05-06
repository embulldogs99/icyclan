<?php
// Connecting, selecting database
$dbconn = pg_connect("host=localhost dbname=postgres user=postgres password=postgres")
    or die('Could not connect: ' . pg_last_error());

// Performing SQL query
$query = 'SELECT * FROM fmi.portfolio';
$result = pg_query($query) or die('Query failed: ' . pg_last_error());

// Printing results in HTML
echo $result;
// Free resultset
pg_free_result($result);

// Closing connection
pg_close($dbconn);
?>
