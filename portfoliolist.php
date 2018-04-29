<?php
$portfolio = pg_connect("host=localhost dbname=postgres user=postgres");
if (!$portfolio) {
    die("Error in connection: " . pg_last_error());
}
// execute query
$sql = "SELECT * FROM fmi.portfolio";
$result = pg_query($portfolio, $sql);
if (!$result) {
    die("Error in SQL query: " . pg_last_error());
}
// iterate over result set
// print each row
while ($row = pg_fetch_array($result)) {
    echo "Ticker: " . $row[0] . "<br />";
    echo "Shares: " . $row[1] . "<br />";
    echo "Price: " . $row[2] . "<br />";
    echo "Value: " . $row[3] . "<br />";
    echo "Target: " . $row[4] . "<br />";
    echo "Exp Return: " . $row[5] . "<br />";
    echo "Exp Value: " . $row[6] . "<br />";
}
// free memory
pg_free_result($result);
// close connection
pg_close($dbh);?>
