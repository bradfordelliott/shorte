<?php
include_once("shorte_source_code.php");

//date_default_timezone_set('America/Toronto');

$g_code_parser = new source_code_t();

function wikify($keyword, $exclude_wikiwords)
{
    return $keyword;
}

function process_link($matches)
{
    $data = $matches[1];

    $count = preg_match("/(.*),(.*)/", $data, $matches);

    if($count > 0)
    {
        $source = trim($matches[1]);
        $label  = trim($matches[2]);
        
        $source = preg_replace("/^\"(.*)\"/", "$1", $source); 
        $label  = preg_replace("/^\"(.*)\"/", "$1", $label); 
        $external = True;

        #print "source = %s, label = %s" % (source, label)
    }
    else
    {
        $source = trim($data);
        $label = $source;

        $source = preg_replace("/->/", "#", $source);
        $label = preg_replace("/(.*?->)/", "", $label);
        $external = False;

        #print "source = %s, label = %s" % (source, label)
    }
    
    /* DEBUG BRAD: To Port
    expr = re.compile("(\$[A-Za-z0-9_]+)", re.DOTALL)
    source = xmlize(expr.sub(self.m_engine._expand_url, source))
    label  = expr.sub(self.m_engine._expand_url, label)
     */

    return array($source, $label, $external);
}

function expand_links($matches)
{
    $result = process_link($matches);
    $source = $result[0];
    $label = $result[1];
    $external = $result[2];

    return sprintf("<a href='%s'>%s</a>", $source, $label);
}

//function expand_anchors(matches)
//{
//
//    (source, label, external) = self._process_link(matches)
//
//    return "<a name='%s'>%s</a>" % (source, label)
//}

function format_links($data)
{
    //// Expand any anchors
    //$data = preg_replace_callback('/\[\[\[(.*?)\]\]\]/', expand_anchors, $data);
       
    // Expand any links
    $data = preg_replace_callback("/\[\[(.*?)\]\]/", "expand_links", $data);

    return $data;
}

function format_action($matches)
{
    $action = $matches[1];

    return "<b>ACTION:</b>$action";
}

function format_table($matches)
{
    $table = $matches[1];

    $rows = explode("\n", $table);
    $html = '<table class="bordered">';

    for($i = 0; $i < count($rows); $i++)
    {
        $row = $rows[$i];

        $row = trim($row);
        if(strlen($row) == 0)
        {
            continue;
        }

        $html .= '<tr>';

        $items = explode('|', $row);

        for($j = 0; $j < count($items); $j++)
        {
            if($i == 0)
            {
                $html .= ('<th>' . $items[$j] . '</th>');
            }
            else
            {
                $html .= ('<td>' . $items[$j] . '</td>');
            }
        } 

        $html .= '</tr>';
    }

    $html .= '</table>';

    return $html; 
}

function format_keywords($language, $source, $exclude_wikiwords)
{
    global $g_code_parser;

    $keywords = $g_code_parser->get_keyword_list($language);

    $output = '';
    $keyword = '';
    $pos_start = 0;


    $source = preg_replace("/\n/", "", $source);
    

    $len = strlen($source);

    //$source = explode("\n", $source);

    for($i = 0; $i < $len; $i++)
    {
        $c = $source[$i];

        // Debug brad - added ord(c) == 46 to get the leeds.write combo
        //if((ord(c) >= 65 and ord(c) < 91) or (ord(c) >= 48 and ord(c) < 58) or (ord(c) >= 97 and ord(c) <= 122) or (ord(c) == 95) or (c == '.' and i < (len(source) - 1) and source[i+1] == ' ')):
        //if((ord(c) >= 65 and ord(c) < 91) or (ord(c) >= 48 and ord(c) < 58) or (ord(c) >= 97 and ord(c) <= 122) or (ord(c) == 95) or (c == '.' and (i < len(source) - 1) and source[i+1] not in (' ', '\n', '\t'))):
        if((ord($c) >= 65 and ord($c) < 91) or (ord($c) >= 48 and ord($c) < 58) or (ord($c) >= 97 and ord($c) <= 122) or (ord($c) == 95) or ($c == '.'))
        {
            $keyword .= $c;
        } 
        else
        {
            if($keyword != '')
            {
                //print "  keyword1: {%s}" % keyword
                //print "  substr:   {%s}" % source[pos_start:i]
                if(array_key_exists($keyword, $keywords))
                {
                    $output .= sprintf("<span class='kw'>%s</span>", $keyword);
                }
                else
                {
                    $output .= wikify($keyword, $exclude_wikiwords);
                }

                $keyword = '';
            }
            
            $pos_start = $i+1;
            $output .= $c;
        }
    }

    if($keyword != '')
    {
        if(array_key_exists($keyword, $keywords))
        {
            $output .= sprintf("<span class='kw'>%s</span>", $keyword);
        }
        else
        {
            $output .= wikify($keyword, $exclude_wikiwords);
        }
        //print "  keyword2 = %s" % keyword
    }
    //print "output = %s\n" % output

    return $output;
}

function format_source_code($language, $tags, $exclude_wikiwords=array(), $show_line_numbers=true)
{
    $allow_line_numbers = 2; //int(self.m_engine.get_config("html", "allow_line_numbers"))
    
    $line_number_div = '';
    $output = '';

    $line = 1;

    // Inline line numbers
    if($allow_line_numbers == 1)
    {
        $output .= '<span class="ln">001  </span>';
    }

    // Line numbers in floating div
    else if($allow_line_numbers == 2)
    {
        $line_number_div .= '001  \n';
    }

    foreach ($tags as $tag)
    {
        $type = $tag["type"];
        $source = $tag["data"];
        
        if(($type == TAG_TYPE_COMMENT) || ($type == TAG_TYPE_MCOMMENT))
        {
            $source = $source.replace("->", "#");
        }

        $source = preg_replace("/&/", "&amp;", $source);
        $source = preg_replace("/</",   "&lt;",  $source);
        $source = preg_replace("/>/",   "&gt;",  $source);
        $source = preg_replace("/\n/",  "",      $source);
        //print "SOURCE: %s" % source
    
    //    // Convert any inline styling blocks
    //    expr = re.compile("@\{(.*?)\}", re.DOTALL);
    //    source = expr.sub(self.parse_inline_styling, source);

        //source = source.strip()

        if($type == TAG_TYPE_CODE)
        {
            if($source != "")
            {
                $source = format_keywords($language, $source, $exclude_wikiwords);
                $output .= $source;
            }
        }
        else if($type == TAG_TYPE_COMMENT or $type == TAG_TYPE_MCOMMENT)
        {
//            source = self._format_links(source)
//            if(self.allow_wikify_comments()):
//                source = self.wikify(source, exclude_wikiwords)
//            output += '<span class="cmt">%s</span>' % source
        }
        else if($type == TAG_TYPE_WHITESPACE)
        {
            //output += '&nbsp;'
            $output .= ' ';
        }
        else if($type == TAG_TYPE_STRING)
        {
            //$output .= '<span class="str">%s</span>' % self.wikify(source, exclude_wikiwords)
            $output .= sprintf("<span class=\"str\">%s</span>", $source); // % self.wikify(source, exclude_wikiwords)
        }
        else if($type == TAG_TYPE_NEWLINE)
        {
            $output .= '<br/>';
            $line += 1;
            //output += "<span class='ln'>%03d&nbsp;&nbsp;</span>" % (line)

            if($allow_line_numbers == 1)
            {
                $output .= sprintf("<span class='ln'>%03d  </span>", $line);
            }
            else if($allow_line_numbers == 2)
            {
                $line_number_div .= sprintf("%03d  \n", $line);
            }
        }
        else
        {
//            print "Skipping tag %s" % source
//            self.exit(-1);
        }
    }

    $html = '';
    if($allow_line_numbers == 2 && $show_line_numbers)
    {
        $html = "<div class='code'>";
        $html .= "<div class='snippet' style='white-space:pre-wrap'>";
        $html .= "<div style='width:4%;float:left;white-space:pre;color:#ccc;'>" . $line_number_div . "</div>";
        $html .= "<div style='width:90%;float:left;white-space:pre-wrap'>" . $output . "</div>";
        $html .= "<div style='clear:both;'></div>";
        $html .= "</div>";
        $html .= "</div>";

    }
    else
    {
        $html = "<div class='snippet' style='white-space:pre-wrap'>" . $output . "</div>";
    }

    return $html;
}

function format_c($matches)
{
    global $g_code_parser;
    $text = $matches[1];

    $tags = $g_code_parser->parse_source_code("c", $text);
    return format_source_code("c", $tags);
}

function format_inline_styling($matches)
{
    $tag = trim($matches[1]);
    $content = trim($matches[2]);

    $style = '';

    $tags = explode("+", $tag);

    foreach ($tags as $tag)
    {
        $tag = trim($tag);

        if($tag == "hl")
        {
            $style .= 'background-color: yellow;';
        }
        else if($tag == "hl2")
        {
            $style .= 'background-color: #00ffff;';
        }
        else if($tag == "b")
        {
            $style .= 'font-weight:bold;';
        }
        else if($tag == "i")
        {
            $style .= 'font-style:italic;';
        }
    }

    $output = "<span style=\"$style\">$content</span>";

    return $output;
}


function strip_indent($input, $indent)
{
    if($indent == 0)
    {
        return $input;
    }

    //print "INPUT=[%s], indent=%d" % (input, indent)

    for($i = 0; $i < $indent+1; $i++)
    {
        if($input[$i] != " ")
        {
            break;
        }
    }

    return substr($input, $i);
}

function parse_block($text)
{
    $lines = explode("\n", $text);

    // Remove any leading blank lines
    foreach ($lines as $line)
    {
        if(strlen($line) == 0)
        {
            unset($lines[$line]);
        }
        else
        {
            break;
        }
    }

    // Figure out the indent of the first line
    $indent = 0;
    for($i = 0; $i < strlen($lines[0]); $i++)
    {
        if($lines[0][$i] == " ")
        {
            $indent += 1;
        }
        else
        {
            break;
        }
    }

    //print "Indent = %d" % indent
    
    $lines_out = array();
    foreach ($lines as $line)
    {
        if(strlen($line) == 0)
        {
            continue;
        }
        array_push($lines_out, strip_indent($line, $indent));
        //lines_out.append(line)
    }

    if(count($lines_out) == 0)
    {
        return "";
    }

    //print "DO I get here? len=%d" % len(lines_out)
    //print lines_out
    
    return implode("\n", $lines_out);
}


function parse_list_child($i, $items, $x=1)
{
    //print "%*sparsing text=%s, i=%d" % (x*3, " ", items[i][0].strip(), i)
    $nodes = array();

    while($i < count($items))
    {
        $item   = $items[$i];
        $indent = $item[1];
        $text   = trim($item[0]);
        $children = NULL;

        //print "%*sitem=%s, indent=%d" % (x*3, " ", text, indent)

        // Check to see if the next element has a greater
        // indent, if it is then it's a child
        if($i+1 < count($items))
        {
            $next_item = $items[$i+1];
            $next_indent = $next_item[1];
            $next_text = trim($next_item[0]);
            
            // If the next node in the list has a smaller
            // indent then we've hit the end of this branch
            if($next_indent < $indent)
            {
                //print "%*sstopping at %s, curr_text = %s" % (x*3, " ", next_text, text)
                //print "%*sAdding node %s" % (x*3, " ", text)
                $node = array();
                $node["text"] = $text;
                array_push($nodes, $node);
                return array($i+1, $nodes);
            }
            // If the next node is indented more than it's
            // a child of this node.
            else if($next_indent > $indent)
            {
                #print "%*sWalking children of %s" % (x*3, " ", text)
                $child = parse_list_child($i+1, $items, $x+1);
                $i = $child[0];
                $children = $child[1];
            }

            // Otherwise we're at the same level so continue
            // adding elements.
            else
            {
                //print "%*sContinue at text=%s,next_text=%s" % (x*3, " ", text, next_text)
                $i += 1;
            }
        }
        else
        {
            $i += 1;
        }
        //print "%*sAdding node %s" % (x*3, " ", text)
        $node = array();
        $node["text"] = $text;

        if($children != NULL)
        {
            if(count($children) > 0)
            { 
                $node["children"] = $children;
                $children = array();
            }
        }

        array_push($nodes, $node);

        // Check the next item in the list and make sure it's not
        // then end of this level
        if($i < count($items))
        {
            $next_item = $items[$i];
            $next_indent = $next_item[1];
            if($next_indent < $indent)
            {
                //print "Next item %s is up one level" % next_item[0].strip()
                $i -= 1;
                break;
            }
        }
   }

   return array($i+1,$nodes);
}


function parse_list($source, $modifiers)
{
    $items = array();
    $item = "";
    $item_indent = 0;

    for($i = 0; $i < strlen($source); $i++)
    {
        if($source[$i] == "-")
        {
            // Look backwards till the first newline
            // to ensure this is a list item and not
            // a dash between two words:
            $j = $i-1;
            $is_list_item = True;

            while($j > 0)
            {
                if($source[$j] == "\n")
                {
                    break;
                }
                else if($source[$j] != " ")
                {
                    $is_list_item = False;
                }
                $j -= 1;
            }

            if(!$is_list_item)
            {
                $item .= $source[$i];
                continue;
            }
            
            //echo "J: $j\n";

            // Output the last item if it exists
            if($item != "")
            {
                //echo "ITEM: indent=$item_indent " . $item . "<br/>";
                array_push($items, array($item, $item_indent));
            }
            $item = "";

            // Figure out the indent level of this item
            $item_indent = 0;
            $j = $i;

            while($j >= 0)
            {
                if($source[$j] == "\n")
                {
                    break;
                }

                $j -= 1;
                $item_indent += 1;
            } 
            //print "indent = $item_indent<br/>";
        }
        else
        {
            $item .= $source[$i];
        }
    }

    if($item != "")
    {
        //echo "ITEM: indent=$item_indent " . $item . "<br/>";
        array_push($items, array($item, $item_indent));
    }

    $child = parse_list_child(0, $items);
    $i = $child[0];
    $list = $child[1];

    //for elem in list:
    //    print elem

    return $list;
}

function parse_textblock($data)
{
    $STATE_NORMAL = 0;
    $STATE_LIST = 1;
    $STATE_CODE = 2;
    $states = array();
    array_push($states, $STATE_NORMAL);

    $segments = array();
    $segment = array();
    $segment["type"] = "text";
    $segment["text"] = "";
    $i = 0;

    //print "DATA: [%s]" % data

    while($i < strlen($data))
    {

        $state = end($states);

        if($state == $STATE_NORMAL)
        {
            if($data[$i] == "-")
            {
                if($i == 0 or $data[$i-1] == "\n")
                {
                    //print "Starting a list, last seg=%s" % segment
                    $i += 1; 
                    array_push($segments, $segment);
                    $segment = array();
                    $segment["type"] = "list";
                    $segment["text"] = "-";
                    array_push($states, $STATE_LIST);
                }
                else
                {
                    $segment["text"] .= $data[$i];
                    $i += 1;
                }
            }
            // Start of a new segment
            else if($data[$i] == "\n" and ($i < strlen($data)-1) and $data[$i+1] == "\n")
            {
                array_push($segments, $segment);
                $segment = array();
                $segment["type"] = "text";
                $segment["text"] = "";
                $i += 2;
            }
            else if($data[$i] == "{" and $data[$i+1] == "{")
            {
                array_push($segments, $segment);
                $segment = array();
                $segment["type"] = "code";
                $segment["text"] = "";
                $i += 2;
                array_push($states, $STATE_CODE);
            }
            else
            {
                $segment["text"] .= $data[$i];
                $i += 1;
            }
        }
        else if($state == $STATE_CODE)
        {
            
            if($data[$i] == "}" and $data[$i+1] == "}")
            {
                $segment["text"] .= "";
                $i += 2;
                array_push($segments, $segment);
                $segment = array();
                $segment["type"] = "text";
                $segment["text"] = "";
                array_pop($states);
            }
            else
            {
                $segment["text"] .= $data[$i];
                $i += 1;
            }
        }
        else if($state == $STATE_LIST)
        {
            if($data[$i] == "\n" and ($i > strlen($data)-2 or $data[$i+1] == "\n"))
            {
                $segment["text"] .= $data[$i];
                $i += 2;
                array_push($segments, $segment);
                array_pop($states);
                $segment = array();
                $segment["type"] = "text";
                $segment["text"] = "";
            }
            else
            {
                $segment["text"] .= $data[$i];
                $i += 1;
            }
        }
    }

    if($segment["text"] != "")
    {
        array_push($segments, $segment);
    }

    //for segment in segments:
    //    print "SEGMENT: \n%s" % segment

    $paragraphs = array();

    foreach ($segments as $segment)
    {
        $indent = 0;
        $text = $segment["text"];
        $type = $segment["type"];

        //print "Segment [%s]" % segment

        for($i = 0; $i < strlen($text); $i++)
        {
            if($text[$i] == ' ')
            {
                $indent += 1;
            }
            else
            {
                break;
            }
        }

        $is_code = False;
        $is_list = False;
        
        // Handle any code blocks detected within the
        // textblock. Code blocks are represented by {{ }}
        if($type == "code")
        {
            $text = parse_block($text);
            $is_code = True;
        }
        else if($type == "list")
        {
            //print "LIST: [%s]" % text

            $elements = parse_list($text, "");

            $text = $elements;
            $is_list = True;
        }

        array_push($paragraphs, array(
            "indent" => $indent,
            "text"   => $text,
            "code"   => $is_code,
            "list"   => $is_list));
    }
    
    return $paragraphs;
}

function format_text($text, $allow_wikify=True, $exclude_wikify=array(), $expand_equals_block=False)
{
    if($text == NULL)
    {
        return "";
    }

    $text = preg_replace_callback('/@table(.*?)---/s', "format_table", $text);
    $text = preg_replace_callback('/@action(.*?)---/s', "format_action", $text);
    $text = preg_replace_callback('/@c(.*?)---/s', "format_c", $text);
    $text = preg_replace_callback('/@\{(.*?),(.*?)\}/', "format_inline_styling", $text);
    $text = preg_replace('/\*\*(.*?)\*\*/', "<i><b>$1</b></i>", $text);
    $text = preg_replace('/\*(.*?)\*/', "<b><b>$1</b></b>", $text);
    $text = preg_replace('/\s_(.*?)_\s/', "<u>$1</u>", $text);
    
    $text = preg_replace("/\n\s*\n/", "<br/><br/>", $text);
    $text = preg_replace("/\\\\n/", '<br/>', $text);

    // make any links or references
    $text = format_links($text);

    /*
    //data = trim_blank_lines(data)

    //#print "DATA: [%s]" % data

    //# Strip trailing lines

    //data = re.sub("\n\s*\n", "<br/><br/>", data)

    //# Replace any \n's with a <br>
    //data = re.sub("\\\\n", "<br/>", data)

    //if(expand_equals_block):
    //    data = re.sub("==+", "<div style='width:20%;border-top:1px solid #ccc;height:1px;'></div>", data)
    //
    //# Hilite any text between **** ****
    //hiliter = re.compile("\*\*\*\*(.*?)\*\*\*\*", re.DOTALL)
    //data = hiliter.sub("<font class='hilite'>\\1</font>", data)

    //# Underline any text between __ __
    //hiliter = re.compile("__(.*?)__", re.DOTALL)
    //data = hiliter.sub("<u>\\1</u>", data)

    //# Underline anything in <<<>>> brackets
    //hiliter = re.compile("\<\<\<(.*?)\>\>\>", re.DOTALL)
    //data = hiliter.sub("<u>\\1</u>", data)
    //
    //# First make any links or references
    //data = self._format_links(data)

    //# Then insert any images. Make sure to add
    //# them to the list of images that need to be
    //# copied over.
    //data = re.sub("<<(.*?),(.*?)(,(.*?))?>>", self.format_inline_image, data)
    //data = re.sub("<<(.*?)>>", self.format_inline_image, data)

    //# Now convert any ** to italics
    //italics = re.compile("\*\*(.*?)\*\*", re.DOTALL)
    //data = italics.sub("<i>\\1</i>", data)
    //
    //# Now convert any *phrase* to bold
    //bold = re.compile("\*(.*?)\*", re.DOTALL)
    //data = bold.sub("<b>\\1</b>", data)

    //# Convert any inline styling blocks
    //expr = re.compile("@\{(.*?)\}", re.DOTALL)
    //data = expr.sub(self.parse_inline_styling, data)
    //
    //if(allow_wikify):
    //    data = self.wikify(data)
    */

    return $text;
}


function format_list_child($elem, $start_tag, $end_tag)
{
    $source = '';
    if(array_key_exists("children", $elem))
    {
        $source .= "<li>" . format_text($elem["text"]);
        $num_children = count($elem["children"]);
        $source .= $start_tag;

        //print "num_children = %d" % num_children
        for($i = 0; $i < $num_children; $i++)
        {
            $source .= format_list_child($elem["children"][$i], $start_tag, $end_tag);
        }

        $source .= $end_tag . "</li>";
    }
    else
    {
        $source .= "<li>" . format_text($elem["text"]) . "</li>";
    }

    return $source;
}

function format_list($list, $ordered=False, $indent=0)
{
    if($indent != 0)
    {
        $style = sprintf(" style='margin-left:%d;' ", indent*10);
    }
    else
    {
        $style = "";
    }

    if(!$ordered)
    {
        $start_tag = sprintf("<ul%s>", $style);
        $end_tag = "</ul>";
    }
    else
    {
        $start_tag = sprintf("<ol%s>", $style);
        $end_tag = "</ol>";
    }

    $source = $start_tag;

    foreach ($list as $elem)
    {
        $source .= format_list_child($elem, $start_tag, $end_tag);
    }

    $source .= $end_tag;

    return $source;
}


function format_textblock($tag)
{
    $paragraphs = $tag["contents"];
    $html = '';

    if(is_array($paragraphs))
    {
        foreach ($paragraphs as $p)
        {
            $indent  = $p["indent"];
            $text    = $p["text"];
            $is_code = $p["code"];
            $is_list = $p["list"];

            //print "Indent: [%d], text: [%s]" % (indent, text)

            if($is_code)
            {
                $style = sprintf("margin-left:%dpx;background-color:#eee;border:1px solid #ccc;", 30);
            }
            else
            {
                $style = sprintf("margin-left:%dpx;", (20 + ($indent * 10)));
            }

            if($is_code)
            {
                $html .= "<div class='code'><div class='snippet' style='white-space:pre'>" . format_text($text) . "</div></div>\n";
            }
            else if($is_list)
            {
                $html .= format_list($p["text"], False, $indent);
            }
            else
            {
                $html .= sprintf("<p style=\"%s\">", $style) . format_text($text) . "</p>\n";
            }
        }
    }
    else
    {
        $html .= "<p>" . format_text($paragraphs) . "</p>\n";
    }

    return $html;
}

function display_text($text)
{
    if(FALSE === strpos($text, "<pre>"))
    {
        $tag = array();
        $tag["contents"] = parse_textblock($text);
        $tag["src"] = $text;

        $html = format_textblock($tag);
    }
    else
    {
        $html = format_text($text);
    }

    return $html;
}

define("SHORTE_STATE_NORMAL",     0);
define("SHORTE_STATE_INTAG",      1);
define("SHORTE_STATE_INMTAGDATA", 2);
define("SHORTE_STATE_INTAGDATA",  3);
define("SHORTE_STATE_ESCAPE",     4);
define("SHORTE_STATE_COMMENT",    5);
define("SHORTE_STATE_MODIFIERS",  6);

class shorte_parser_t
{
    private function search_and_replace($text)
    {
        //return $m_engine->search_and_replace($text);
        return $text;
    }
    
    private function parse_tag_data($tag_name, $input, $i)
    {
        $tag_data = "";
        $tag_modifier = "";

        $STATE_NORMAL     = 0;
        $STATE_COMMENT    = 1;
        $STATE_MODIFIER   = 2;
        $STATE_MULTILINE_STRING = 3;

        $states = Array();
        array_push($states, $STATE_NORMAL);

        // Skip any leading whitespace
        while($input[$i] == ' ' or $input[$i] == '\t')
        {
            $i = $i + 1;
        }

        if($input[$i] == ':')
        {
            array_push($states, $STATE_MODIFIER);
            $i += 1;
        }
        else if($input[$i] == '\n')
        {
            $this->m_current_line += 1;
            $i += 1;
        }

        while($i < strlen($input))
        {

            if($input[$i] == '\n')
            {
                $this->m_current_line += 1;
            }

            $state = $states[-1];

            if($state == STATE_NORMAL)
            {

                if(!$this->tag_is_source_code($tag_name))
                {
                    // parse any comments
                    if($input[$i] == '#')
                    {
                        array_push($states, STATE_COMMENT);
                        $i = $i + 1;
                        continue;
                    }
                }
                
                // DEBUG BRAD: This is an attempt to skip
                //             inline @ so they don't need to
                //             be escaped
                //if(input[i] == '@'):
                if(($i == 0 and $input[$i] == '@') or ($input[$i] == '@' and $input[$i-1] == '\n'))
                {
                    if($input[$i+1] == '{')
                    {
                        $tag_data .= $input[i];
                    }
                    else
                    {
                        break;
                    }
                }  
                // If we hit an escape sequence then skip it and
                // the next character
                else if($input[$i] == '\\')
                {
                    // DEBUG BRAD: This is an attempt to strip
                    //             escape sequence backslashes
                    if($this->tag_is_source_code($tag_name))
                    {
                        $tag_data .= $input[$i];
                    }
                    // DEBUG BRAD: Added this on Oct 19, 2013
                    else
                    {
                        $tag_data .= $input[$i];
                    }

                    $tag_data .= $input[$i+1];
                    $i+=2;
                    continue;
                }
                else
                {
                    $tag_data .= $input[$i];
                }
            }
            else if($state == STATE_MODIFIER)
            {
                if($input[$i] == '\n')
                {
                    array_pop($states);
                }
                else if(substr($input, $i, 3) == "'''")
                {
                    #print "DO I GET HERE?"
                    $tag_modifier += '"';
                    array_push($states, STATE_MULTILINE_STRING);
                    $i = $i + 3;
                    continue;
                }
                else
                {
                    $tag_modifier += $input[$i];
                }
            }
            else if($state == STATE_MULTILINE_STRING)
            {
                if(substr($input, $i, 3) == "'''")
                {
                    array_pop($states);
                    $i = $i + 2;
                    #print "MODIFIER: [%s]" % tag_modifier
                    $tag_modifier .= '"';
                }
                else
                {
                    $tag_modifier .= $input[$i];
                }
            }
            else if($state == STATE_COMMENT)
            {
                if($input[$i] == '\n')
                {
                    array_pop($states);
                }
            }

            $i = $i + 1;
        }

        //print "TAG:\n  DATA: [%s]\n  MODIFIERS: [%s]" % (tag_data, tag_modifier)

        return Array($i, $tag_data, $tag_modifier);
        
    }

    public function parse($input)
    {
        $tags = Array();
        $states = Array();

        array_push($states, SHORTE_STATE_NORMAL);

        $tag_name = "";
        $tag_data = "";
        $tag_modifiers = "";

        $i = 0;

        while($i < strlen($input))
        {
            $state = $states[-1];

            if($state == SHORTE_STATE_IN_TAG)
            {
                if($input[i] == ' ' or $input[i] == ':' or $input[i] == '\t' or $input[i] == '\n')
                {
                    list($i, $tag_data, $tag_modifiers) = $this->parse_tag_data($tag_name, $input, $i);
                    $tags = $this->parse_tag($title, $tag_name, $tag_data, $tag_modifiers);
                    
                    $excluded = $this->append_tags_if_not_excluded($tags, $excluded, $tag_name, $page["tags"]);

                    $tag_name = "";
                    $tag_data = "";
                }
                else
                {
                    $tag_name .= $input[$i];
                }
            }
            else if($state == SHORTE_STATE_NORMAL)
            {
                if($input[$i] == '#')
                {
                    array_push($states, SHORTE_STATE_COMMENT);
                }
                // DEBUG BRAD: Assume it's a tag only if it starts at the beginning of a line
                else if(($i == 0 and $input[$i] == '@') or ($input[$i] == '@' and $input[$i-1] == '\n'))
                {
                    //print "CHARS: %s,%s" % (input[i], input[i+1])
                    if($input[$i+1] == '{')
                    {
                        print "DO I GET HERE?";
                    }
                    else
                    {
                        //print "Here"
                        if($tag_name != "" and $tag_data != "")
                        {
                            list ($i, $tag_data, $tag_modifiers) = $this->parse_tag_data($tag_name, $input, $i);

                            $tags = $this->parse_tag($title, $tag_name, $tag_data, $tag_modifiers);
                        
                            $excluded = $this->append_tags_if_not_excluded($tags, $excluded, $tag_name, $page["tags"]);
                        }

                        $tag_name = "";
                        $tag_data = "";
                        
                        array_push($states, SHORTE_STATE_INTAG);
                    }
                }
                else if($input[$i] == '\\')
                {
                    //tag_data += input[i]
                    array_push($states, SHORTE_STATE_ESCAPE);
                }
            }
            else if($state == SHORTE_STATE_ESCAPE)
            {
                $tag_data .= $input[$i];
                array_pop($states);
            }
            else if($state == SHORTE_STATE_COMMENT)
            {
                if($input[$i] == '\n')
                {
                    array_pop($states);
                }
            }

            $i = $i + 1;
        }

        if($tag_data != "")
        {
            if($tag_name != "")
            {

                list ($i, $tag_data, $tag_modifiers) = $this->parse_tag_data(
                        $tag_name, $input, $i);
                    
                $tags = $this->parse_tag($title, $tag_name, $tag_data, $tag_modifiers);

                $excluded = $this->append_tags_if_not_excluded($tags,
                    $excluded, $tag_name, $page["tags"]);
            }
            else
            {
                
                if($i < strlen($input))
                {
                    //print "snippet: %s, i = %d, len = %d" % (input[i:-1], i, len(input))
                    //(i, tag_data, tag_modifiers) = self._parse_tag_data("p", input, i)
                    //tags = self._parse_tag(title, tag_name, tag_data, tag_modifiers)
                    //
                    //excluded = self.__append_tags_if_not_excluded(tags, excluded, tag_name, page["tags"])
                }
            }
        }

        return display_text($input);
    }
}

?>

