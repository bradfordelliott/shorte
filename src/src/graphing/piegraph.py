#!/usr/bin/python
import sys
import re
import libs.cairo_access as cairo_access
from libs.cairo_access import *
import math

from graph import graph_t


class pie_graph_t(graph_t):

    def __init__(self, width, height):

        graph_t.__init__(self,width,height)

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
        maxY = self.get_max_ycoordinate();

        # DEBUG BRAD: This is a temporary hack
        #maxX = 10

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
                            text = label,
                            font_family="Helvetica")
         
        graph.draw_text(x = (left + (right - left)/2),
                        y = bottom + 35,
                        font_color = "#000000",
                        text       = self.xaxis["label"])
    
    def draw_data(self):

        #maxX = self.get_max_xcoordiate()
        #maxY = self.get_max_ycoordinate();
        graph = self.graph

        #yincrement = (maxY/10.0)
        #
        #if(1 == self.xaxis["autoscale"]):
        #    xincrement = (maxX/10.0)
        #else:
        #    xincrement = maxX/10.0;

        #if(xincrement == 0):
        #    xincrement = 1
        #    maxX = 1;
        #if(yincrement == 0):
        #    yincrement = 1;
        #    maxY = 1;
        #
        #yAxisIncrements = maxY/yincrement;
        #xAxisIncrements = maxX/xincrement;
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

        center_x = x + ((width - (2*padding))/2)
        center_y = y + ((height - (2*padding))/2)

        #print "Ellipse"
        #print "  x: %d" % x
        #print "  y: %d" % y
        #print "  bottom: %d" % bottom
        #print "  top:    %d" % top

        ellipse_width = width   - (2*padding)
        ellipse_height = height - (2*padding)
        
        graph.draw_ellipse(x-2.5, y-2.5, width=width-(2*padding)+5, height=height-(2*padding)+5,
                    line_pattern=1,
                    font_color="#00000",
                    font_size=10,
                    text=None,
                    line_color="#c0c0c0",
                    background_color="#ff0000",
                    line_weight=5.0,
                    start_angle = 0.0,
                    end_angle = 2.0*math.pi)

        # First figure out the total of all values
        total = 0
        for dataset in self.datasets:
            keys = self.datasets[dataset]["data"].keys()
            for key in keys:
                total += self.datasets[dataset]["data"][key]

        print "TOTAL: %f" % total

        colors = []
        colors.append("#f0f0f0")
        colors.append("#00ff00")
        colors.append("#0000ff")
        colors.append("#ff00ff")

        angle = 0
        last_angle = angle

        cindex = 0
        for dataset in self.datasets:
            keys = self.datasets[dataset]["data"].keys()
            for key in keys:
                value = self.datasets[dataset]["data"][key]

                percentage = value/total

                last_angle = angle
                angle += percentage * (2 * math.pi)

                px = center_x + ((ellipse_width/2)  * math.cos(angle))
                py = center_y + ((ellipse_height/2) * math.sin(angle))

                color = colors[cindex]
                cindex += 1

                graph.draw_ellipse(x, y,
                    width=ellipse_width,
                    height=ellipse_height,
                    line_pattern=1,
                    font_color="#00000",
                    font_size=10,
                    text=None,
                    line_color="#c0c0c0",
                    background_color=colors[cindex],
                    line_weight=1.6,
                    start_angle=last_angle,
                    end_angle=angle)
                
        angle = 0
        last_angle = 0

        # Now draw the label for each data set
        for dataset in self.datasets:
            keys = self.datasets[dataset]["data"].keys()
            for key in keys:
                value = self.datasets[dataset]["data"][key]

                percentage = value/total

                last_angle = angle
                angle += percentage * (2 * math.pi)

                # The point on the circumference of the ellipse
                px = center_x + ((ellipse_width/2)  * math.cos(angle))
                py = center_y + ((ellipse_height/2) * math.sin(angle))

                # Calculate the half way point through this
                # slice of the pie
                half_way = last_angle + (percentage * math.pi)

                # Now calculate the point mid way between the center
                # of the ellipse and it's circumference
                pxh = center_x + ((ellipse_width/4)  * math.cos(half_way))
                pyh= center_y + ((ellipse_height/4) * math.sin(half_way))

                graph.draw_text(pxh,pyh-5,
                                font_color = "#000000",
                                text       = "%2.2f" % value,
                                font_size  = 10)
    
    def draw_graph(self, path):
        graph_t.draw_graph(self)
        
        self.draw_data()
        self.draw_legend()
        self.draw_title()


        self.graph.image.write_to_png(path, self.width+280, self.height+110)
