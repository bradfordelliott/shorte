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
from src.shorte_defines import *
import graph
from graph import *

def min(one, two):
    if(one < two):
        return one
    return two
    
SPACER = '<img class="spacer" src="images/spacer.gif"></img>';

def make_tooltip(tooltip):
    tooltip = tooltip.replace('\n', ' ')
    tooltip = tooltip.replace('\t', ' ')
    tooltip = tooltip.replace('\\n', '\\<br\\>')
    tooltip = tooltip.replace('{', '\\<')
    tooltip = tooltip.replace('}', '\\>')
    tooltip = tooltip.replace('\\t', SPACER)
    tooltip = tooltip.replace('"', "\\'")
    tooltip = tooltip.replace('"', "&apos;")
    tooltip = tooltip.replace("'", "&apos;")
    tooltip = re.sub(" +", " ", tooltip)

    return tooltip
     
        
def generate_diagram(events, title, description, target_width, target_height, base_file_name):

    cairo = cairo_t(5000, 5000)

    # Read the configuration file
    RIGHT_BREAK = 0x01
    LEFT_BREAK  = 0x02
    RESERVED    = 0x04
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
                x += gap_between_actors + 50
                sources.append(event["to"])
    
    num_events = len(events)
    height = y + num_events * gap_between_events
    width = x
    
    for source in sources:

       # Draw veritical lines for each source point
       cairo.draw_line(
           x1=keys[source]["x"],
           y1=y,
           x2=keys[source]["x"],
           y2=height,
           line_color="red",
           background_color="white",
           line_weight=1.5,
           line_pattern=4)
       
       # Draw the source label for each line
       cairo.draw_text(
           x=keys[source]["x"],
           y=y-20,
           text=source,
           text_anchor="middle")
       
       # Draw a litle beige rectangle at the
       # start of each source line.
       cairo.draw_rect(
           x=keys[source]["x"]-6,
           y=y,
           width=12,
           height=10,
           background_color="#E8DFAC",
           line_color="#c0c0c0",
           line_width=2)
    
    event_count = 0
    
    y += 30
    height += 30
   
    spacer = '''<img src='images/spacer.gif' width='10' height='1'></img>'''

    # Now walk through the list of fields parsed from the input XML and generate
    # the output SVG XML as well as the associated HTML table row describing
    # the fields.
    for event in events:
        etype = event["type"]

        if(etype in ("action", "loop")):
            name   = event["name"]
            desc   = event["desc"]
            
            tooltip = make_tooltip(event["desc"])
            
            source = event["from"]

            ex = keys[source]["x"] - 10
            ey = y-(gap_between_events/2)
            eheight = (gap_between_events-10)
            ewidth=20

            cairo.draw_rect(
                x=keys[source]["x"] - 10,
                y=y-(gap_between_events/2),
                width=ewidth,
                height=gap_between_events - 10,
                background_color="#e8dfac",
                line_color="#c0c0c0",
                rounding=5,
                line_width=3,
                text="%s" % event_count,
                )

            # Draw an arrow from the end of the event back to
            # the start point to indicate the loop
            if(etype == "loop"):
                points = []
                points.append((ex+(ewidth/2),ey - 10))
                points.append((ex+50+(ewidth/2),ey - 10))
                points.append((ex+50+(ewidth/2),ey+eheight + 10))
                points.append((ex+(ewidth/2),ey+eheight + 10))
                points.reverse()
                #cairo.draw_curve(points=points,line_color="#0000ff",line_weight=1.5)
                cairo.draw_lines(points=points,line_color="#0000ff",line_weight=1.5)

                cairo.draw_text(
                    x=keys[source]["x"] + 75,
                    y=y - 10,
                    text=event["name"],
                    text_anchor="middle",
                    font_color="#a0a0a0")
            else:
                cairo.draw_text(
                    x=keys[source]["x"],
                    y=y+5,
                    text=event["name"],
                    text_anchor="middle",
                    font_color="#a0a0a0")
                
            
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

            #cairo.draw_text(
            #    x=text_position,
            #    y=y-5,
            #    font_color="#000000",
            #    text="WTF%s" % event_count,
            #    text_anchor="middle")
        
            y += gap_between_events
            #continue

        # Message
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
           
            # Replace the new line and tab characters with their HTML
            # equivalents
            tooltip = make_tooltip(event["desc"])
            spacer = "<img src=\\'images/spacer.gif\\' width=\\'10\\' height=\\'1\\'></img>"
           
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
                line_weight=3.0,
                text="%s" % event_count,
                font_color="#a0a0a0")
            
            xml += '''
<text text-anchor="middle" font-family="Courier New" 
      font-size="14" font-weight="bold" x="%d" y="%d" fill="#A0A0A0" >
%d
</text>
''' % (text_position, (y - (gap_between_events - 34)), event_count)
            
            event_count+=1

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
                y=y-18,
                font_color="#808080",
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
                        font_color="#00ff00",
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
    
    event_table += "</table>"
    image_map += "</map>"
    
    scratch_dir = shorte_get_scratch_path()
    image_name = scratch_dir + "/" + base_file_name

    # Convert the result into a PNG file
    output_file = image_name + ".png"

    #print "Creating %s" % output_file

    #cmd = 'java -Djava.awt.headless=true -jar %s -bg 1.255.255.255 -w %d -h %d -m image/png %s' % (BATIK, width, height, base_file_name + ".svg")
    #print "CMD: [%s]" % cmd
    #result = os.popen(cmd)

    #cairo.image.write_to_png("test2.png", width, height)
    cairo.image.write_to_png(output_file, width, height)
    
    return (output_file, image_map, events_table)
    

