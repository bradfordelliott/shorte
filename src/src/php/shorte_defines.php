<?php

define('TAG_TYPE_CODE',       0);
define('TAG_TYPE_STRING',     1);
define('TAG_TYPE_COMMENT',    2);
define('TAG_TYPE_MCOMMENT',   3);
define('TAG_TYPE_WHITESPACE', 4);
define('TAG_TYPE_NEWLINE',    5);

define('STATE_NORMAL',    1);
define('STATE_COMMENT',   2);
define('STATE_STRING',    3);
define('STATE_MSTRING',   4);
define('STATE_MCOMMENT',  5);
define('STATE_MODIFIER',  6);


function trim_blank_lines($source)
{
    $lines = explode("\n", $source);

    if(count($lines) == 1)
    {
        return $source;
    }

    $output = '';

    // Find the index of first non-blank line
    $start = 0;
    for($i = 0; $i < count($lines); $i++)
    {
        $tmp = trim($lines[$i]);
        if($tmp != "")
        {
            break;
        }
        $start += 1;
    }

    //print "Start = %d" % start

    // Find the index of the last non-blank line
    $end = count($lines)-1;
    for($i = count($lines)-1; $i > 0; $i--) // in range(len(lines)-1, 0, -1):
    {
        $tmp = trim($lines[$i]);

        if($tmp != "")
        {
            break;
        }
        $end -= 1;
    }

    //print "End = %d" % end

    for($i = $start; $i < $end+1; $i++) // i in range(start, end+1):
    {
        $output .= $lines[$i] . "\n";
    }

    return $output;
}


function trim_leading_indent($source)
{
    $source = trim_blank_lines($source);

    // Now figure out the indent of the first line
    $i = 0;
    $leading_indent = '';
    while($i < strlen($source) and $source[$i] == " ")
    {
        $leading_indent .= $source[$i];
        $i += 1;
    }

    // Trim any leading indent from each line
    $lines = explode("\n", $source);
    $lines_out = array();

    foreach ($lines as $line)
    {
        $line = preg_replace(sprintf("/^%s/", $leading_indent), "", $line);
        array_push($lines_out, $line);
    }
    
    $source = implode("\n", $lines_out);

    return $source;
}

?>
