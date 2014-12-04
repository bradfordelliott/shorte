#!/usr/bin/python
import sys
import re
if __name__ == "__main__":
    sys.path.append("../..")
sys.path.append(".")
import libs.cairo_access as cairo_access
from libs.cairo_access import *
import math

from graph import graph_t


class timeline_graph_t(graph_t):

    def __init__(self, width, height):

        graph_t.__init__(self,width,height)
    
    
    def get_max_xcoordiate(self):
        maxX = 0
        
        for dataset in self.datasets:
            for key in self.datasets[dataset]["data"]:
                if(key > maxX):
                    maxX = key

        maxX = (math.ceil(maxX /10.0)) * 10;

        #print "MAX X: %d" % maxX
        
        return maxX


    def draw_yaxis(self):

        return
        
        maxX = self.get_max_xcoordiate()
        maxY = 10

        graph = self.graph
       
        if(maxY == 0):
            maxY = 1
    
        increment = maxY/10
        y_axis_increments = maxY/increment
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
        maxY = 10

        if(maxX == 0):
            maxX = 1
        
        graph = self.graph
        
        height = self.height
        width = self.width
        top = self.top
        left = self.left
        right = self.right
        bottom = self.bottom
        
        increment = 3;
        
        #if(1 == self.xaxis["autoscale"]):
        #    increment = math.ceil(maxX/10.0)
        
        #print "increment: %d" % increment
        #print "maxX: %d" % maxX
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

            labels = self.xaxis["labels"]

            if(labels != None and len(labels) > count):
                label = labels[count]

            
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
        maxX = self.get_max_xcoordiate()
        maxY = 10
        graph = self.graph

        yincrement = (maxY/10)
        
        #if(1 == self.xaxis["autoscale"]):
        #    xincrement = (maxX/10)
        #else:
        xincrement = 1.0
        #print "x_increment: %d" % xincrement

        if(xincrement == 0):
            xincrement = 1
            maxX = 1;
        if(yincrement == 0):
            yincrement = 1;
            maxY = 1;
        
        yAxisIncrements = maxY/yincrement;
        xAxisIncrements = maxX/xincrement;

        #print "increments: %d" % xAxisIncrements

        height = self.height
        width = self.width
        top = self.top
        left = self.left
        right = self.right
        bottom = self.bottom


        num_data_points = 0

        for dataset in self.datasets:
            for key in self.datasets[dataset]["data"]:
                num_data_points += 1


        pointer_offset_increment = (height/2.0)/(num_data_points-2)
        #pointer_offset_increment = 30
        pointer_offset = pointer_offset_increment
        
        for dataset in self.datasets:
            for key in self.datasets[dataset]["data"]:
                pointer_offset += pointer_offset_increment
            
        graph.draw_line(left, bottom - (height/2), right, bottom - (height/2), line_color="#d0d0d0")

        for dataset in self.datasets:
            prevx = left;
            prevy = bottom;
            color = self.datasets[dataset]["color"]
            #print "COLOR: %s" % color
            points = []

            #for key in (sort {$a <=> $b} keys(%{$self->{DATASETS}{$dataset}{"data"}}))
            for key in self.datasets[dataset]["data"]:
                xvalue = key;
                #print "xvalue = %d" % xvalue
                yvalue = self.datasets[dataset]["data"][key]["val"]
                
                #print "x = %d, y = %d" % (xvalue, yvalue)
                # DEBUG BRAD: Currently the value, need more
                #             information than just the y value
                evalue = yvalue
                elabel = self.datasets[dataset]["data"][key]["label"]

                # For timeline the y-value is always 5. The
                # data argument is the size/scale of the event.
                yvalue = 5

                x = (((xvalue/(1.0*xincrement))/(1.0 * maxX)) * width) + left;
                y = bottom - (((yvalue/(1.0*yincrement))/(1.0*maxY)) * height);

                #print "x = %d" % x
                point = (x,y);
                points.append(point)
        
                
                # Now mark the points
                #    We need to scale them so that they are not too large.
                #    basically, if we are a width of 600 then we will use
                #    diameter 5 and scale down based on this ratio
                diameter = ((evalue * width)/800);
                diameter_outer = diameter + 10
                
                graph.draw_ellipse(x = x - (diameter_outer/2),
                                   y = y - (diameter_outer/2),
                                   width  = diameter_outer,
                                   height = diameter_outer,
                                   line_color = color,
                                   background_color = color)

                color = color.replace("#", "")
                r = int(color[0:2],16)
                g = int(color[2:4],16)
                b = int(color[4:],16)
                #print "color: r=%s, g=%s, b=%s" % (r,g,b)

                new_color = "#%02x%02x%02x" % (r*0.6, g*0.6, b*0.6)

                #print "new_color: %s" % new_color
                
                graph.draw_ellipse(x = x - (diameter/2),
                                   y = y - (diameter/2),
                                   width = diameter,
                                   height = diameter,
                                   line_color = color,
                                   background_color = new_color)
                
                if(self.draw_values()):
                    graph.draw_text(x = x,
                                  y = y - 10,
                                  font_color = color,
                                  text       = "%2.2f" % yvalue,
                                  font_size  = 7)
                prevx = x;
                prevy = y;

                # Draw the angled line pointing to the
                # event at a 45 degree angle up and to the right.
                x1 = x
                y1 = y
                len = pointer_offset
                pointer_offset -= pointer_offset_increment
                x2 = x1 + (len * math.sin(graph.to_radians(45)))
                y2 = y1 - (len * math.cos(graph.to_radians(45)))
                
                graph.draw_line(x1,y1,x2,y2, line_color=color, line_pattern=2)

                # Now complete the pointer to the end of the graph area
                graph.draw_line(x2,y2,right + 60,y2, line_color=color, line_pattern=2)
        
                #label = "%2.2f" % evalue
                #(text_width, text_height) = graph.image.text_extents(label)
                (text_width, text_height) = graph.image.text_extents(elabel)

                # Draw some text at the end of the pointer
                graph.draw_text(x=right + 65, y=y2 - (text_height/2), font_color=color, text=elabel, font_size=7)
               
            #graph.draw_curve(points      = points,
            #                 line_color  = color,
            #                 line_weight = 1)
    
    def draw_graph(self, path):
        graph_t.draw_graph(self)
        
        self.draw_yaxis()
        self.draw_xaxis()
        self.draw_data()
        self.draw_legend(yoffset = -20, xoffset=100)
        self.draw_title()

        self.graph.image.write_to_png(path, self.width+280, self.height+110)


if __name__ == "__main__":
    timeline = timeline_graph_t(800, 400)
    timeline.set_title("This is a test graph", "A test timeline with some data")
    
    labels = []
    for i in range(1977, 2020, 3):
        labels.append("%d" % i)
    timeline.set_xaxis("Time",   "red", labels=labels)
    timeline.set_yaxis("Y-Axis", "red")

    base = 1977
        
    d = {
            1977 - base: {"val" : 5,   "label" : "Test 0",  "caption" : "Test 1"},
            1978 - base: {"val" : 20,  "label" : "Test 1",  "caption" : "Test 2"},
            1979 - base: {"val" : 35,  "label" : "Test 6",  "caption" : "Test 3"},
            1989 - base: {"val" : 55,  "label" : "Test 4",  "caption" : "Test 4"},
            1993 - base: {"val" : 100, "label" : "Test 12", "caption" : "Test 5"},
            1999 - base: {"val" : 10,  "label" : "Test 14", "caption" : "Test 6"},
            2001 - base: {"val" : 100, "label" : "Test 15", "caption" : "Test 7"}
        }
    timeline.add_data_set(d, "one", color="c0c0c0")
    
    d2 ={
            1980 - base: {"val" : 6,   "label" : "Test 2",  "caption" : "Test 2"},
            1983 - base: {"val" : 4,   "label" : "Test 3",  "caption" : "Test 3"},
            1985 - base: {"val" : 15,  "label" : "Test 7",  "caption" : "Test 7"},
            2007 - base: {"val" : 100, "label" : "Test 15", "caption" : "Test 7"}
        }
    
    timeline.add_data_set(d2, "two", color="f00000")
    timeline.draw_graph("timeline.png")
