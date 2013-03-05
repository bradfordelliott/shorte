#!/usr/bin/python
#+----------------------------------------------------------------------------
#|
#| SCRIPT:
#|   Sequence diagram generator
#|
#| DESCRIPTION:
#|   Contains routines used to generate diagrams of MP messages in a
#|   manner similar to the TCP and IP header diagrams.
#|
#| CREATED:
#|   18 Apr 2005 (Brad Elliott)
#|     
#+----------------------------------------------------------------------------
import os
import re
import shorte_defines
from shorte_defines import *
import graph
from graph import *

def min(one, two):
    if(one < two):
        return one
    return two
        
def generate_diagram(events, title, description, target_width, target_height, base_file_name):

    cairo = cairo_t(5000, 5000)

    # Read the configuration file
    #BATIK = shorte_get_config("paths", "path.batik")
    RIGHT_BREAK = 0x01
    LEFT_BREAK  = 0x02
    RESERVED    = 0x04
    SPACER = '<img class="spacer" src="images/spacer.gif"></img>';
    ALIGNMENT = 32;
    
    eventPoints = {}
    arcpointoffsetx = 75
    
    #if(defined($data->{diagram}->{arcpointoffsetx}))
    #{
    #   $arcpointoffsetx = $data->{diagram}->{arcpointoffsetx};
    #}
    #
    #my $arcpointoffsety = 0;
    #
    #if(defined($data->{diagram}->{arcpointoffsety}))
    #{
    #   $arcpointoffsety = $data->{diagram}->{arcpointoffsety};
    #}
    
    # Convert new lines and tabs in the input XML into <br> tag and and
    # empty image respectively. This allows minimal formatting of the
    # description field.
    description = description.replace("\n", "<br>")
    description = description.replace("\t", SPACER)
    description = description.replace("{", "<")
    description = description.replace("}", ">")

    xml = ''
    
    image_map = '<map name="%s">' % base_file_name

    # Create an XML header for the generated SVG file
    xml_header = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="680" height="300" viewBox="0 0 680 300" 
       preserveAspectRatio="xMidYMid meet" zoomAndPan="disable" 
       xmlns="http://www.w3.org/2000/svg" 
       xmlns:xlink="http://www.w3.org/1999/xlink">
'''

    xml_header += '''
       <defs>
         <marker fill="red" stroke="red" id="lineend" 
                 viewBox="0 0 50 50" refX="0" refY="5" 
                 markerUnits="strokeWidth" 
                 markerWidth="50" markerHeight="50" 
                 orient="auto">
           <path d="M 0 0 L 10 5 L 0 10 z" />
         </marker>
         <marker id="End"
                 viewBox="0 0 50 50" refX="0" refY="5" 
                 markerUnits="strokeWidth" 
                 markerWidth="50" markerHeight="50" 
                 orient="auto">
           <path d="M 0 0 L 10 5 L 0 10 z" />
         </marker>
         <marker id="Start" 
                 viewBox="0 0 50 50" refX="0" refY="5" 
                 markerUnits="strokeWidth" 
                 markerWidth="50" markerHeight="50" 
                 orient="auto">
           <path d="M 10 0 L 0 5 L 10 10 Lz" />
         </marker>
       </defs>
'''

    x = 50
    y = 40
    gap_between_actors = 150
    gap_between_events = 70

    events_table = '''- Event | Source | Sink | Name | Description
'''
    
    event_table = '''<table class="bordered">'''
                      
    event_table += '''
<tr class="header">
    <th colspan=5>Sequence Diagram</th>
</tr>
<tr class="header">
    <td class="header" width="100">Event</td>
    <td class="header" width="50">Source</td>
    <td class="header" width="50">Sink</td>
    <td class="header" width="150">Name</td>
    <td class="header" width="">Description</td>
</tr>
'''
    
    sources = []
    keys = {}
    
    for event in events:
        if(event["type"] == "message"):
            if(not keys.has_key(event["from"])):
                keys[event["from"]] = {}
                keys[event["from"]]["set"] = 1
                keys[event["from"]]["x"] = x
                x += gap_between_actors
                sources.append(event["from"])
            if(not keys.has_key(event["to"])):
                keys[event["to"]] = {}
                keys[event["to"]]["set"] = 1
                keys[event["to"]]["x"] = x
                x += gap_between_actors
                sources.append(event["to"])
    
    num_events = len(events)
    height = y + num_events * gap_between_events
    width = x
    
    for source in sources:
       xml += '''<line x1="%d" y1="%d"  x2="%d" y2="%d" fill="white" stroke="red" stroke-width="1.5" stroke-dasharray="5,3,2"/>
''' % (keys[source]["x"], y, keys[source]["x"], height)

       cairo.draw_line(
           x1=keys[source]["x"],
           y1=y,
           x2=keys[source]["x"],
           y2=height,
           line_color="red",
           background_color="white",
           line_weight=1.5,
           line_pattern=4)
       
       xml += '''
<text text-anchor="middle" font-family="Courier New"
      font-size="14" font-weight="bold" x="%d" y="%d" fill="#909090">
%s
</text>
''' % (keys[source]["x"], y-14, source)
       
       cairo.draw_text(
           x=keys[source]["x"],
           y=y-15,
           text=source,
           text_anchor="middle")
       
       xml += '''
<rect x="%d" y="%d" rx="2" ry="2"
      width="12" 
      height="10" 
      fill="#E8DFAC" stroke="#c0c0c0"
      stroke-width="2"/>
''' % (keys[source]["x"] - 6, y)

       cairo.draw_rect(
           x=keys[source]["x"]-6,
           y=y,
           width=12,
           height=10,
           background_color="#E8DFAC",
           line_color="#c0c0c0",
           line_weight=2)
    
    event_count = 0
    
    y += 30
    height += 30
    
    # Now walk through the list of fields parsed from the input XML and generate
    # the output SVG XML as well as the associated HTML table row describing
    # the fields.
    for event in events:
        etype = event["type"]
    
        if(etype == "action"):
            name   = event["name"]
            desc   = event["desc"]
            
            tooltip = event["desc"]

            tooltip = tooltip.replace('\n', ' ')
            tooltip = tooltip.replace('\t', ' ')
            tooltip = tooltip.replace('\\n', '\\<br\\>')
            tooltip = tooltip.replace('{', '\\<')
            tooltip = tooltip.replace('}', '\\>')
            
            spacer = '''<img src='images/spacer.gif' width='10' height='1'></img>'''

            tooltip = tooltip.replace('\\t', SPACER)
            tooltip = tooltip.replace('"', "\\'")
    
            source = event["from"]
            xml += '''
<rect x="%d" y="%d" rx="4" ry="4"
      width="20"
      height="%d"
      fill="#f0f0f0" stroke="#c0c0c0"
      stroke-width="3"/>
''' % (keys[source]["x"] - 10, y - gap_between_events/2, gap_between_events - 10)

            cairo.draw_text(
                x=keys[source]["x"] - 10,
                y=y-gap_between_events/2,
                width=20,
                height=gap_between_events - 10,
                background_color="#f0f0f0",
                line_color="#c0c0c0")
            
            text_position = keys[source]["x"]
    
            image_map += '''
<area shape="rectangle" coords="%d,%d,%d,%d" href="#%s_%d"
      onMouseover="ddrivetip('%s')"
      onMouseout="hideddrivetip()">
''' % (keys[source]["x"] - 5,
       y - (gap_between_events/2), keys[source]["x"] + 7, y + (gap_between_events/2) - 8,
       base_file_name, event_count, tooltip)

            # Update the HTML table describing the field
            if(event_count & 0x01):
                event_table += '''
         <tr class="alternaterow">
'''
            else:
                event_table += '''
        <tr>
'''

            events_table += '''- %s | %s | | %s | %s
''' % ("[[[%s_%d,%d]]]" % (base_file_name, event_count, event_count), event["from"], event["name"], event["desc"])

            event_table += '''
    <td class="inline"><a name="%d">%d</a></td>
    <td class="inline">%s</td>
    <td class="inline">&nbsp;</td>
    <td class="inline">%s</td>
    <td class="inline">%s</td>
''' % (event_count, event_count, event["from"], event["name"], event["desc"])
    
            event_count+=1
       
            xml += '''
<text text-anchor="middle" font-family="Courier New"
      font-size="14" font-weight="bold"
      x="%d" y="%d" fill="#A0A0A0">
%d
</text>
''' % (text_position, y - 5, event_count)

            cairo.draw_text(
                x=text_position,
                y=y-5,
                font_color="#000000",
                text="%s" % event_count,
                text_anchor="middle")
        
            y += gap_between_events
            continue

        else:
            source = event["from"]
            target = event["to"]
            name   = event["name"]
            desc   = event["desc"]
            
            # Update the HTML table describing the field
            if(event_count & 0x01):
                event_table += '''
        <tr class="alternaterow">
'''
            else:
                event_table += '''
        <tr>
'''
            event_count+=1
           
            # Replace the new line and tab characters with their HTML
            # equivalents
            tooltip = event["desc"]

            tooltip = tooltip.replace('\n', ' ')
            tooltip = tooltip.replace('\t', ' ')
            tooltip = tooltip.replace('\\n', '\\<br\\>')
            tooltip = tooltip.replace('{', '\\<')
            tooltip = tooltip.replace('}', '\\>')

            spacer = "<img src=\\'images/spacer.gif\\' width=\\'10\\' height=\\'1\\'></img>"
            tooltip = tooltip.replace('\\t', SPACER)
            tooltip = tooltip.replace('"', "&apos;")
            tooltip = tooltip.replace("'", "&apos;")
            tooltip = re.sub(" +", " ", tooltip)
           
            event["desc"] = event["desc"].replace('\\n', '<br>')
            event["desc"] = event["desc"].replace('\\t', SPACER)
            event["desc"] = event["desc"].replace('{', '<')
            event["desc"] = event["desc"].replace('}', '>')
           
            event_table += '''
    <td class="inline"><a name="%d">%d</a></td>
    <td class="inline">%s</td>
    <td class="inline">%s</td>
''' % (event_count, event_count, event["from"], event["to"])

            events_table += "- [[[%s_%d, %d]]] | %s | %s" % (base_file_name, event_count, event_count, event["from"], event["to"]) 
           
            if(not event.has_key("link")):
                event_table += '''<td class="inline">%s</td>''' % event["name"]
                events_table += "| %s" % event["name"]
            else:
                event_table += '''<td class="inline"><a href="%s">%s</a></td>''' % (event["link"], event["name"])
                events_table += "| %s" % event["name"]

            event_table += '''<td class="inline">%s</td></tr>''' % (event["desc"])
            events_table += "| %s\n" % (event["desc"]) 
           
            offset = -10

            text_position = min(keys[target]["x"], keys[source]["x"]) +  \
                            abs(keys[target]["x"] - keys[source]["x"])/2
            
            if(keys[target]["x"] > keys[source]["x"]):
                offset = 10
           
            if(keys[source].has_key("lasty")):
                xml += '''
    <rect x="%d" y="%d" rx="4" ry="4"
          width="12"
          height="%d" 
          fill="#f0f0f0" stroke="#c0c0c0"
          stroke-width="3"/>
''' % (keys[source]["x"], y - (gap_between_events - 5), gap_between_events - 10)

                cairo.draw_rect(
                    x=keys[source]["x"],
                    y=y - (gap_between_events - 5),
                    width=12,
                    height=gap_between_events - 10,
                    background_color="#f0f0f0",
                    line_color="#c0c0c0")

                image_map += '''
    <area shape="rectangle" coords="%d,%d,%d,%d"
          href="#%s_%d" 
          onMouseover="ddrivetip('blah blah')" onMouseout="hideddrivetip()">
''' % (keys[source]["x"] - 5,
       y - (gap_between_events-5), keys[source]["x"] + 7,
       y - (gap_between_events-5) + gap_between_events-10, base_file_name, event_count)

           
            image_map += '''
<area shape="circle" coords="%d,%d,12"
      href="#%s_%d"
      onMouseover="ddrivetip('%s')" onMouseout="hideddrivetip()">
''' % (text_position, (y-(gap_between_events-29)), base_file_name, event_count, tooltip)

           
            width_name = len(event["name"]) * 5
           
            if(event.has_key("link")):
                image_map += '''
<area shape="rectangle" coords="%d,%d,%d,%d" href="%s">
''' % ((text_position - width_name/2),
        y - (gap_between_events-35),
        (text_position + width_name/2),
        y+5,
        link)
           
            xml += '''
<circle cx="%d" cy="%d" r="12" fill="#F0F0F0" stroke="#c0c0c0" stroke-width="2.5" />
''' % (text_position, y - (gap_between_events-30))
            
            cairo.draw_ellipse(
                x=text_position-(25/2),
                y=(y-(gap_between_events-25)-7),
                width=25,
                height=25,
                background_color="#f0f0f0",
                line_color="#c0c0c0",
                line_weight=3.0)
            
            xml += '''
<text text-anchor="middle" font-family="Courier New" 
      font-size="14" font-weight="bold" x="%d" y="%d" fill="#A0A0A0" >
%d
</text>
''' % (text_position, (y - (gap_between_events - 34)), event_count)

            cairo.draw_text(
                x=text_position,
                y=(y - (gap_between_events - 25)),
                text="%s" % event_count,
                font_color="#a0a0a0",
                text_anchor="middle")

           
            color = "black"
            if(event.has_key("link")):
                color = "blue"
            
            xml += '''
<text text-anchor="middle" font-family="Courier New"
      font-size="12" x="%d" y="%d" fill="%s">
%s
</text>
''' % (text_position, y-10, color, name)

            cairo.draw_text(
                x=text_position,
                y=y-10,
                font_color=color,
                text=name,
                text_anchor="middle")
           
            if((event.has_key("type")) and (event["type"] == "bidir")):
                xml += '''<path d="M %d %d L %d %d"
                              fill="black" stroke="black"
                              stroke-width="1"
                              marker-start="url(#Start)"
                              marker-end="url(#End)"/>
''' % (keys[source]["x"], y, keys[target]["x"] - offset, y)

                cairo.draw_line(
                    x1=keys[source]["x"],
                    y1=y,
                    x2=keys[target]["x"],
                    y2=y,
                    line_color="#000000",
                    background_color="#000000",
                    arrow_end=2)

            else:
                xml += '''<path d="M %d %d L %d %d"
                            fill="black" stroke="black"
                            stroke-width="1"
                            marker-end="url(#End)"/>
''' % (keys[source]["x"], y, keys[target]["x"] - offset, y)

                #print "Here: x1=%d, y1=%d, x2=%d, y2=%d" % (
                #    keys[source]["x"],
                #    y,
                #    keys[target]["x"],
                #    y)
                
                cairo.draw_line(
                    x1=keys[source]["x"],
                    y1=y,
                    x2=keys[target]["x"],
                    y2=y,
                    line_color="#000000",
                    background_color="#000000",
                    arrow_end=2)

           
            if(event.has_key("fromlabel")):
                #print "Event type for fromlabel: $name, x=" + $keys{$source}{"x"} . " y=" . $y ."\n";
                event_points[event["fromlabel"]]["x"] = keys[source]["x"]
                event_points[event["fromlabel"]]["y"] = y
           
            if(event.has_key("tolabel")):
                event_points[event["tolabel"]]["x"] = keys[target]["x"] - offset
                event_points[event["tolabel"]]["y"] = y
           
#           if(defined($event->{fromlink}))
#           {
#              my $marker = $event->{fromlink};
#              my $markerx = $eventPoints{$marker}{"x"};
#              my $markery = $eventPoints{$marker}{"y"};
#              
#              $xml .= "<path d=\"M " . ($keys{$source}{"x"}) . " " .
#                            ($y) . " S " .
#                            ($keys{$source}{"x"} + $markerx + 35). " " .
#                            ($y - (($y-$markery)/2)) . ", $markerx $markery\" " .
#                            "fill=\"none\" stroke=\"red\" " .
#                            "stroke-width=\"1\" stroke-dasharray=\"5,3,2\" " .
#                            "marker-end=\"url(#End)\"/>";
#           }
#           
#           if(defined($event->{tolink}))
#           {
#              my $marker = $event->{tolink};
#              my $markerx = $eventPoints{$marker}{"x"};
#              my $markery = $eventPoints{$marker}{"y"};
#              
#              my $arcpoint = $event->{arcpoint} = 
#              $xml .= "<path d=\"M " . ($keys{$target}{"x"}+5) . " " .
#                            ($y+5) . " S " .
#                            ($keys{$target}{"x"} + $markerx + $arcpointoffsetx). " " .
#                            ($y + (($y-$markery)/2) + $arcpointoffsety) . ", " . ($markerx + 10) . " " . ($markery + 5) . "\" " .
#                            "fill=\"none\" stroke=\"red\" " .
#                            "stroke-width=\"1\" stroke-dasharray=\"5,3,2\" " .
#                            "marker-end=\"url(#lineend)\"/>";
#              
                if(event.has_key("tolinknote")):
                    strings = event["tolinknote"].split("\n")

                    xml += '''
<text text-anchor="middle" font-family="Courier New"
      font-size="10" x="%d", y="%d" fill="green">
''' (keys[target]["x"] + markerx + arcpointoffsetx, abs(y - ((y-markery)/2)))

                    cairo.draw_text(
                        x = keys[target]["x"] + markerx + arcpointoffsetx,
                        y = abs(y - ((y-markery)/2)),
                        text_anchor = "middle")
                    
                    offset = 0
                    for string in strings:
                        xml += '''
<tspan x="%d" y="%d">
%s
</tspan>
''' % (keys[target]["x"] + markerx + (arcpointoffsetx/2), abs(y - ((y-markery)/2)) + offset, string)

                        offset += 15
                    
                    xml += "</text>"

            y += gap_between_events
#        }
#    
#        #$keys{$target}{"lasty"} = $y;
#        #undef($keys{$source}{"lasty"});
#    }
    
    
    event_table += "</table>"
    image_map += "</map>"
    xml += "</svg>\n"
    
    xml_header = xml_header.replace("680", "%d" % width)
    xml_header = xml_header.replace("300", "%d" % height)
    
    hdiagram = open(base_file_name + ".svg", "wb")
    hdiagram.write(xml_header)
    hdiagram.write(xml)
    hdiagram.close()
    
    # Convert the result into a PNG file
    output_file = base_file_name + ".png"
    
    #cmd = 'java -Djava.awt.headless=true -jar %s -bg 1.255.255.255 -w %d -h %d -m image/png %s' % (BATIK, width, height, base_file_name + ".svg")
    #print "CMD: [%s]" % cmd
    #result = os.popen(cmd)
        
    cairo.image.write_to_png("test2.png", width, height)
    
    return (output_file, image_map, events_table)
    

