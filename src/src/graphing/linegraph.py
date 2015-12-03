#!/usr/bin/python
import sys
import re
import math

from graph import graph_t


class line_graph_t(graph_t):

    def __init__(self, width, height, bg_color=None, line_color=None):

        graph_t.__init__(self,width,height, bg_color, line_color)

    def __del__(self):
        graph_t.__del__(self)

    def draw_yaxis(self):
        
        max_x = self.get_max_xcoordinate()
        max_y = self.get_max_ycoordinate()
        min_y = self.get_min_ycoordinate()
        min_x = self.get_min_xcoordinate()

        graph = self.graph
       
        if(max_y == 0):
            max_y = 1

        yrange = max_y - min_y
    
        increment = yrange/10.0
        y_axis_increments = int(yrange/increment)
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
                label = max_y - ((count * yrange * increment)/(yrange))
            
            graph.draw_text(x = left - 40,
                            y = vertical_position + 4,
                            font_color = "#000000",
                            font_size = 8,
                            text     = "%.2f" % label)
        
        label = self.yaxis["label"]
        (twidth, theight) = graph.text_extents(label)

        graph.draw_text(x = left - 60,
                        y = top + (bottom - top)/2 + (twidth/2),
                        font_color = "#000000",
                        text       = label,
                        text_orientation = "vertical")
   
    def draw_xaxis(self):
        max_x = self.get_max_xcoordinate();
        min_x = self.get_min_xcoordinate();

        if(max_x == 0):
            max_x = 1
        
        graph = self.graph
        
        height = self.height
        width = self.width
        top = self.top
        left = self.left
        right = self.right
        bottom = self.bottom
        x_range = max_x - min_x
        
        increment = x_range/10.0;
        
        x_axis_increments = int(math.ceil(x_range/increment))
        
        # Figure out the zero crossing
        if(min_x < 0):
            xvalue = abs(min_x)
            x = left + ((((xvalue)/(increment))/(x_range/increment)) * width);
            graph.draw_line(x1 = x,
                            y1 = top,
                            x2 = x,
                            y2 = bottom,
                            line_color = "#ff0000",
                            background_color = "#FFFFFF",
                            line_weight = 1,
                            line_pattern = 1)

        # Draw the X-Axis
        for count in range(0, x_axis_increments + 1):
            horizontal_position = left + (count * (width/(x_range/increment)));
        
            if(count != x_axis_increments and count != 0):
               graph.draw_line(x1 = horizontal_position,
                               y1 = top,
                               x2 = horizontal_position,
                               y2 = bottom,
                               line_color = "#909090",
                               background_color = "#FFFFFF",
                               line_pattern = 1)
               
               graph.draw_line(x1 = horizontal_position,
                               y1 = bottom - 5,
                               x2 = horizontal_position,
                               y2 = bottom + 5,
                               line_color = "#C0C0C0")
        
            if(0):
               label = math.ceil((count * x_range * increment)/(x_range))
            else:
               label = min_x + (count * x_range * increment)/(x_range)
            
            graph.draw_text(x = horizontal_position - 3, 
                            y = bottom + 15,
                            font_color = "#000000",
                            #background_color = "#FFFFFF",
                            text = label,
                            font_family="Helvetica")

        label = self.xaxis["label"]
        (twidth, theight) = graph.text_extents(label)

        graph.draw_text(x = (left + (right - left)/2) - (twidth/2) ,
                        y = bottom + 35,
                        font_color = "#000000",
                        text       = label)
    
    def draw_data(self):
        max_x = self.get_max_xcoordinate()
        max_y = self.get_max_ycoordinate()
        min_x = self.get_min_xcoordinate()
        min_y = self.get_min_ycoordinate()
        graph = self.graph

        y_range = max_y - min_y
        x_range = max_x - min_x
        
        yincrement = (y_range/10.0)
        
        if(1 == self.xaxis["autoscale"]):
            xincrement = (x_range/10.0)
        else:
            xincrement = x_range/10.0

        if(xincrement == 0):
            xincrement = 1
            max_x = 1;
        if(yincrement == 0):
            yincrement = 1;
            max_y = 1;
        
        xAxisIncrements = int(math.ceil(x_range/xincrement))
        yAxisIncrements = int(math.ceil(y_range/yincrement))
        #yAxisIncrements = y_range/yincrement;
        #xAxisIncrements = x_range/xincrement;
        height = self.height
        width = self.width
        top = self.top
        left = self.left
        right = self.right
        bottom = self.bottom
        
        #print "Y axis increments: %d" % yAxisIncrements
        #print "X axis increments: %d" % xAxisIncrements
        
        for dataset in self.datasets:
            prevx = left;
            prevy = bottom;
            color = self.datasets[dataset]["color"]
            points = []
            startp = None
            endp   = None

            #for key in (sort {$a <=> $b} keys(%{$self->{DATASETS}{$dataset}{"data"}}))
            keys = self.datasets[dataset]["data"].keys()
            keys.sort()

            for key in keys:

                xvalue = key - min_x
                yvalue = self.datasets[dataset]["data"][key] - min_y
                
                #print "x = %d, y = %d" % (xvalue, yvalue)
                
                x = (((xvalue/xincrement)/10.0) * width) + left;
                y = bottom - (((yvalue/yincrement)/10.0) * height);

                if(None == startp):
                    startp = (x,bottom)

                point = (x,y);
                points.append(point)
        
                #print "x = %d, y = %d" % (x, y)
                #$graph->drawLine({"x1" => $prevx,
                #                  "y1" => $prevy,
                #                  "x2" => $x,
                #                  "y2" => $y,
                #                  "line-color" => $color,
                #                  "line-weight" => 1});
                
                
                # Now mark the points
                #    We need to scale them so that they are not too large.
                #    basically, if we are a width of 600 then we will use
                #    diameter 5 and scale down based on this ratio
                diameter = ((5 * width)/800);
                
                graph.draw_ellipse(x = x - (diameter/2),
                                   y = y - (diameter/2),
                                   width = diameter,
                                   height = diameter,
                                   line_color = color,
                                   background_color = color)
                
                if(self.draw_values()):
                    graph.draw_text(x = x,
                                  y = y - 10,
                                  font_color = color,
                                  text       = "%2.2f" % yvalue,
                                  font_size  = 7)
                prevx = x;
                prevy = y;

            endp = (x,bottom)
            graph.draw_curve(points      = points,
                             line_color  = color,
                             line_weight = 1.5,
                             start_point = startp,
                             end_point   = endp,
                             fill        = self.filled)
    
    def draw_graph(self, path):

        self.calculate_dimensions()

        graph_t.draw_graph(self)
        self.draw_yaxis()
        self.draw_xaxis()
        self.draw_data()
        self.draw_legend()
        self.draw_title()


        self.graph.image.write_to_png(path, self.orig_width, self.orig_height)
