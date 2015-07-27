#!/usr/bin/python
import sys
import re
import math

from graph import graph_t

class bar_graph_t(graph_t):

    def __init__(self, width, height, bg_color, line_color):

        graph_t.__init__(self, width, height, bg_color, line_color)

    def draw_yaxis(self):
        max_y = self.get_max_ycoordinate()
        min_y = self.get_min_ycoordinate()

        graph = self.graph
       
        if(max_y == 0):
            max_y = 1

        y_range = (max_y - min_y)
    
        increment = y_range/10.0
        y_axis_increments = int(y_range/increment)
        height = self.height
        width = self.width
        top = self.top
        left = self.left
        right = self.right
        bottom = self.bottom

        # Figure out the zero crossing
        if(min_y < 0):
            yvalue = abs(min_y)
            y = bottom - ((((yvalue)/(increment))/y_axis_increments) * height);
            graph.draw_line(x1 = left,
                            y1 = y,
                            x2 = right,
                            y2 = y,
                            line_color = "#ff0000",
                            background_color = "#FFFFFF",
                            line_weight = 1,
                            line_pattern = 1)
            
        
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
                label = min_y
            else:
                label = max_y - ((count * y_range * increment)/(y_range))
            
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
        max_x = self.get_max_xcoordinate()
        min_x = self.get_min_xcoordinate()

        if(max_x == 0):
            max_x = 1

        graph = self.graph
        
        height = self.height
        width = self.width
        top = self.top
        left = self.left
        right = self.right
        bottom = self.bottom
        
        increment = max_x/10.0;
        
        if(1 == self.xaxis["autoscale"]):
            increment = math.ceil(max_x/10)
        
        xAxisIncrements = int(max_x/increment)
        
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
               label = math.ceil((count * max_x * increment)/(max_x))
            else:
               label = (count * max_x * increment)/(max_x)
            
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
        max_x = self.get_max_xcoordinate();
        max_y = self.get_max_ycoordinate();
        min_x = self.get_min_xcoordinate();
        min_y = self.get_min_ycoordinate();
        graph = self.graph

        x_range = max_x - min_x
        y_range = max_y - min_y
        
        yincrement = (y_range/10.0);
        if(1 == self.xaxis["autoscale"]):
            xincrement = (x_range/10.0);
        else:
            xincrement = x_range/10.0;
        
        y_axis_increments = (y_range/yincrement);
        x_axis_increments = (x_range/xincrement);
        height = self.height
        width = self.width
        top = self.top
        left = self.left
        right = self.right
        bottom = self.bottom
        numdatasets = len(self.datasets)

        #print "x_axis_increments: %d" % xAxisIncrements
        #print "y_axis_increments: %d" % yAxisIncrements

        numpoints = 0
        for dataset in self.datasets:
            numpoints += len(self.datasets[dataset]["data"])
        
        #print "Num data sets: %d" % numdatasets
        #print "Width: %d" % width
        #print "xaxisincremnts: %d" % xAxisIncrements
        barwidth = (right-left)/(30*numdatasets)
        #print "barwidth: %d" % ((right-left) / (30 * numdatasets))
        offset = 0

        # The zero-crossing is the bottom
        bottom = bottom + ((((min_y)/(yincrement))/y_axis_increments) * height);

        for dataset in self.datasets:
            #numpoints = len(self.datasets[dataset]["data"])
            color = self.datasets[dataset]["color"]
            barheight = 0;
            
            #print "bar width   = $barwidth\n";
            #print "xincrements = $xAxisIncrements\n";
            #print "width = $width\n";

            for key in self.datasets[dataset]["data"]:
                # Need to round to the whole number because
                # plotting fractions on a bar graph don't make sense
                xvalue = "%.0f" % (key - min_x)
                yvalue = self.datasets[dataset]["data"][key]

                #x = (((int(xvalue)/int(xincrement))/10.0) * width) + left + offset;
                #y = bottom - (((int(yvalue)/int(yincrement))/10.0) * height);
                x = (((float(xvalue)/(xincrement))/x_axis_increments) * width) + left + offset;
                y = bottom - ((((yvalue)/(yincrement))/y_axis_increments) * height);
                #print("x = $x, y = $y\n");
        
                barheight = bottom - y;
                
                graph.draw_rect(x = x,
                                y = y,
                                width = barwidth,
                                height = barheight,
                                line_color = "#000000",
                                background_color = color);
        
                #if($self->draw_values())
                #{
                #    $graph->drawText({"x" => $x,
                #                      "y" => $y - 10,
                #                      "font-color" => $color,
                #                      "text"       => sprintf("%2.2f", $yvalue),
                #                      "font-size"  => 7});
                #}
                
            offset += barwidth;

    def draw_graph(self, path):
        
        self.calculate_dimensions()

        graph_t.draw_graph(self)

        self.draw_yaxis()
        self.draw_xaxis()
        self.draw_data()
        self.draw_legend()
        self.draw_title()


        self.graph.image.write_to_png(path, self.orig_width, self.orig_height)

