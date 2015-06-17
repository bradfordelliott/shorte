#!/usr/bin/python
import sys
import re
import libs.cairo_access as cairo_access
from libs.cairo_access import *
import math

from graph import graph_t

class memorymap_graph_t(graph_t):

    def __init__(self, width, height):
        
        width = 600
        self.padding = 30
        self.block_width = 100

        graph_t.__init__(self, width, height)

    def draw_data(self):
        
        graph = self.graph
        height = self.height
        width = self.width
        top = self.top
        left = self.left
        right = self.right
        bottom = self.bottom

        padding = self.padding

        # Top left coordinate
        x = (left   + padding)  + ((right - left) / 2) - (width/2)
        y = (bottom + padding)  + ((top-bottom) / 2) - (height/2)

        
        rect_width  = width  - (2*padding)
        rect_height = height - (2*padding)

        #rect_width = self.block_width

        numdatasets = len(self.datasets)
        total = 0
        end_of_last = 0
        dindex = 0

        # Step through the memory map and determine the
        # total memory span.
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
        w=200

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

                h = rect_height * (percentage)
                graph.draw_rect(w+20, y, w, h, background_color="#b0b0b0", text="Reserved")
                y += h

            start = dataset["start"]
            end   = dataset["end"]
            value = (end-start)+1
            percentage = value/(total*1.0)

            h = rect_height * (percentage)

            graph.draw_rect(w+20, y, w, h, background_color=color, text=label)

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
            

    def draw_graph(self, path):
        graph_t.draw_graph(self)

        self.draw_data()
        self.draw_legend()
        self.draw_title()

        self.graph.image.write_to_png(path, self.width+280, self.height+110)

