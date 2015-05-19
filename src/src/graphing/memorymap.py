#!/usr/bin/python
import sys
import re
import libs.cairo_access as cairo_access
from libs.cairo_access import *
import math

from graph import graph_t

class memorymap_graph_t(graph_t):

    def __init__(self, width, height):

        graph_t.__init__(self, width, height)

    def draw_yaxis(self):
        maxX = self.get_max_xcoordiate()
        maxY = self.get_max_ycoordinate()

        graph = self.graph
       
        if(maxY == 0):
            maxY = 1
    
        increment = maxY/10.0
        y_axis_increments = int(maxY/increment)
        height = self.height
        width = self.width
        top = self.top
        left = self.left
        right = self.right
        bottom = self.bottom
        
        # Draw the Y-Axis
        for count in range(0, y_axis_increments + 1):

            vertical_position = top + (count * (height/y_axis_increments))
            
            #print "count = %d, vertical_pos = %d" % (count, vertical_position)
            
            if(count != y_axis_increments and count != 0):
                graph.draw_line(x1 = left,
                               y1 = vertical_position,
                               x2 = right,
                               y2 = vertical_position,
                               line_color = "#909090",
                               background_color = "#FFFFFF",
                               line_weight = 1,
                               line_pattern = 1)
                
                graph.draw_line(x1 = left - 5,
                                y1 = vertical_position,
                                x2 = left + 5,
                                y2 = vertical_position,
                                line_color = "#C0C0C0",
                                line_weight = 1)
    
            if(count == y_axis_increments):
                label = 0
            else:
                label = maxY - ((count * maxY * increment)/(maxY))
            
            graph.draw_text(x = left - 40,
                            y = vertical_position + 4,
                            font_color = "#000000",
                            font_size = 8,
                            text     = "%.2f" % label)
        
        graph.draw_text(x = left - 60,
                        y = top + (bottom - top)/2,
                        font_color = "#000000",
                        text       = self.yaxis["label"],
                        text_orientation = "vertical")

    def draw_xaxis(self):
        maxX = self.get_max_xcoordiate();

        if(maxX == 0):
            maxX = 1
        
        graph = self.graph
        
        height = self.height
        width = self.width
        top = self.top
        left = self.left
        right = self.right
        bottom = self.bottom
        
        increment = maxX/10.0;
        
        if(1 == self.xaxis["autoscale"]):
            increment = math.ceil(maxX/10)
        
        xAxisIncrements = int(maxX/increment)
        
        # Draw the X-Axis
        for count in range(0, xAxisIncrements + 1):
            horizontalPosition = left + (count * (width/xAxisIncrements));
        
            if(count != xAxisIncrements and count != 0):
               graph.draw_line(x1 = horizontalPosition,
                               y1 = top,
                               x2 = horizontalPosition,
                               y2 = bottom,
                               line_color = "#909090",
                               background_color = "#FFFFFF",
                               line_pattern = 1)
               
               graph.draw_line(x1 = horizontalPosition,
                               y1 = bottom - 5,
                               x2 = horizontalPosition,
                               y2 = bottom + 5,
                               line_color = "#C0C0C0")
        
            if(0):
               label = math.ceil((count * maxX * increment)/(maxX))
            else:
               label = (count * maxX * increment)/(maxX)
            
            graph.draw_text(x = horizontalPosition - 3, 
                            y = bottom + 15,
                            font_color = "#000000",
                            #background_color = "#FFFFFF",
                            text = label)
         
        graph.draw_text(x = (left + (right - left)/2),
                        y = bottom + 35,
                        font_color = "#000000",
                        text       = self.xaxis["label"])

    def draw_data(self):
        
        graph = self.graph
        height = self.height
        width = self.width
        top = self.top
        left = self.left
        right = self.right
        bottom = self.bottom

        padding = 40

        # Top left coordinate
        x = (left   + padding)  + ((right - left) / 2) - (width/2)
        y = (bottom + padding)  + ((top-bottom) / 2) - (height/2)

        
        rect_width = width   - (2*padding)
        rect_height = height - (2*padding)

        numdatasets = len(self.datasets)
        total = 0
        end_of_last = 0
        dindex = 0

        for dataset in self.datasets:
            color   = self.datasets[dataset]["color"]
            dataset = self.datasets[dataset]["data"]
            start = dataset["start"]

            # If there is a gap between this
            # section and the last make sure we add
            # it.
            if(dindex > 0 and (start-end) > 1):
                rstart = end+1
                rend   = start-1
                value = (rend-rstart)+1
                total += value/4

            end   = dataset["end"]
            total += (end-start)+1
            dindex += 1
        
        cindex = 0
        dindex = 0
        start = 0
        end = 0

        for dataset in self.datasets:
            label = dataset
            color = self.datasets[dataset]["color"]
            dataset = self.datasets[dataset]["data"]
            start = dataset["start"]
            
            # If there is a gap between this
            # section and the last make sure we draw
            # it and mark it as reserved. We'll scale it
            # down so it doesn't take up too much of the diagram.
            if(dindex > 0 and (start-end) > 1):
                rstart = end+1
                rend   = start-1
                value = (rend-rstart)+1
                value = value/4
                percentage = value/(total*1.0)

                w=200
                h = rect_height * (percentage)
                graph.draw_rect(220, y, w, h, background_color="#b0b0b0", text="Reserved")
                y += h

            start = dataset["start"]
            end   = dataset["end"]
            value = (end-start)+1
            percentage = value/(total*1.0)

            w = 200
            h = rect_height * (percentage)

            graph.draw_rect(220, y, w, h, background_color=color, text=label)

            graph.draw_text(x = 140, 
                        y = y,
                        font_color = "#000000",
                        font_family= "Courier",
                        text       = "%x" % start)
            
            graph.draw_text(x = 140, 
                        y = y+h-10,
                        font_color = "#000000",
                        font_family="Courier",
                        text       = "%x" % end)
            y += h
            dindex += 1
            
        ##print "Num data sets: %d" % numdatasets
        ##print "Width: %d" % width
        ##print "xaxisincremnts: %d" % xAxisIncrements
        #barwidth = (right-left)/(30*numdatasets)
        ##print "barwidth: %d" % ((right-left) / (30 * numdatasets))
        #offset = 0

        #for dataset in self.datasets:
        #    #numpoints = len(self.datasets[dataset]["data"])
        #    prevx = left;
        #    prevy = bottom;
        #    color = self.datasets[dataset]["color"]
        #    barheight = 0;
        #    
        #    #print "bar width   = $barwidth\n";
        #    #print "xincrements = $xAxisIncrements\n";
        #    #print "width = $width\n";

        #    for key in self.datasets[dataset]["data"]:
        #        # Need to round to the whole number because
        #        # plotting fractions on a bar graph don't make sense
        #        xvalue = "%.0f" % key
        #        yvalue = self.datasets[dataset]["data"][key]

        #        #x = (((int(xvalue)/int(xincrement))/10.0) * width) + left + offset;
        #        #y = bottom - (((int(yvalue)/int(yincrement))/10.0) * height);
        #        x = (((float(xvalue)/(xincrement))/xAxisIncrements) * width) + left + offset;
        #        y = bottom - ((((yvalue)/(yincrement))/yAxisIncrements) * height);
        #        #print("x = $x, y = $y\n");
        #
        #        barheight =bottom - y;
        #        
        #        graph.draw_rect(x = x,
        #                        y = y,
        #                        width = barwidth,
        #                        height = barheight,
        #                        line_color = "#000000",
        #                        background_color = color);
        #
        #        #if($self->draw_values())
        #        #{
        #        #    $graph->drawText({"x" => $x,
        #        #                      "y" => $y - 10,
        #        #                      "font-color" => $color,
        #        #                      "text"       => sprintf("%2.2f", $yvalue),
        #        #                      "font-size"  => 7});
        #        #}
        #        
        #        prevx = x;
        #        prevy = y;
        #    offset += barwidth;

    def draw_graph(self, path):
        graph_t.draw_graph(self)

        #self.draw_yaxis()
        #self.draw_xaxis()
        self.draw_data()
        self.draw_legend()
        self.draw_title()

        self.graph.image.write_to_png(path, self.width+280, self.height+110)

