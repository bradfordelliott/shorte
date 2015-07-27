#!/usr/bin/python
import sys
import re
import math

from graph import graph_t


class pie_graph_t(graph_t):

    def __init__(self, width, height,bg_color,line_color):

        graph_t.__init__(self,width,height,bg_color,line_color)

    def draw_yaxis(self):
        
        maxX = self.get_max_xcoordinate()
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
        maxX = self.get_max_xcoordinate();
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
        '''This method draws the data that forms part of
           the pie graph'''

        #maxX = self.get_max_xcoordinate()
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

        #print "TOTAL: %f" % total

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

                color = self.m_colors[cindex]
                cindex += 1

                graph.draw_ellipse(x, y,
                    width=ellipse_width,
                    height=ellipse_height,
                    line_pattern=1,
                    font_color="#00000",
                    font_size=10,
                    text=None,
                    line_color="#c0c0c0",
                    background_color=color,
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
    
    
    def legend_width(self):
        
        self.graph.image.save()
        self.graph.image.set_font_size(10)

        # The minimum width is the legend title
        (width, height) = self.graph.text_extents(self.m_legend_title)
        width += 10
        
        self.graph.image.set_font_size(8)

        legend_pad = 40 + 20

        for dataset in self.datasets:
            (text_width, text_height) = self.graph.text_extents(dataset)
            text_width += legend_pad

            if(text_width > width):
                width = text_width
           
            keys = self.datasets[dataset]["data"]
            for point in keys:
                value = self.datasets[dataset]["data"][point]
            
                (text_width, text_height) = self.graph.text_extents(dataset)
                text_width += legend_pad + 15
            
                if(text_width > width):
                    width = text_width

        self.graph.image.restore()

        return width

    def draw_legend(self, yoffset=50, xoffset=10):
       graph = self.graph
       
       top = self.top
       right = self.right
       y = top + yoffset
          
       # First draw the legend title
       graph.draw_text(x = right + xoffset,
                       y = y,
                       font_color = "#000000",
                       text       = "Legend")
       y += 24
    
       cindex = 0
       #for dataset (sort {$a cmp $b}  keys(%{$self->{DATASETS}}))
       for dataset in self.datasets:

           color = self.m_colors[cindex]

           # Figure out how many points are in the set
           points = len(self.datasets[dataset]["data"])
       
           # Draw the data set
           #graph.draw_rect(
           #    x = right + xoffset + 5,
           #    y = y,
           #    width = 20,
           #    height = 20,
           #    background_color = color,
           #    line_color = color)
           graph.draw_text(
               x = right + xoffset + 5,
               y = y+2,
               font_size = 10,
               font_color = color,
               text       = dataset)

           y += 20     

           # Now draw each sub-block
           keys = self.datasets[dataset]["data"]
           keys = sorted(keys)

           for point in keys:
               color = self.m_colors[cindex]
               value = self.datasets[dataset]["data"][point]
           
               graph.draw_rect(
                   x = right + xoffset + 15,
                   y = y,
                   width = 10,
                   height = 10,
                   background_color = color,
                   line_color = color)

               graph.draw_text(
                   x = right + xoffset + 30,
                   y = y+2,
                   font_size=6,
                   font_color = "#000000",
                   text="%s = %s" % (point, value))
               y += 15
               cindex += 1

           y += 10

    def draw_graph(self, path):

        self.calculate_dimensions()

        graph_t.draw_graph(self)
        
        self.draw_data()
        self.draw_legend()
        self.draw_title()


        self.graph.image.write_to_png(path, self.orig_width, self.orig_height)
