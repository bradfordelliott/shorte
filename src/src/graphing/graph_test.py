#!/usr/bin/python
import sys
import re
sys.path.append("../../libs")
sys.path.append("libs")
import cairo_access
from cairo_access import *
import math

import linegraph
import bargraph

lgraph = linegraph.line_graph_t(800,600)
lgraph.set_title("This is a test graph", "A test line graph with some data")
lgraph.set_xaxis("X-Axis", "red", 0, 10, 1)
lgraph.set_yaxis("Y-Axis", "red", 0, 10, 1)
    
d = {0:1, 1:3, 4:5, 6:4, 7:4, 8:3, 10:8}
lgraph.add_data_set(d, "one", color="red")

d2 = {2:1, 3:3, 4:8, 6:7, 7:9, 8:2, 10:1}
lgraph.add_data_set(d2, "two", color="blue")

lgraph.draw_graph("line.png")


bgraph = bargraph.bar_graph_t(800,600)
bgraph.set_title("This is a test graph", "A test bar graph with some data")
bgraph.set_xaxis("X-Axis", "red", 0, 10, 1)
bgraph.set_yaxis("Y-Axis", "red", 0, 10, 1)
    
d = {0:1, 1:3, 4:5, 6:4, 7:4, 8:3, 9:8}
bgraph.add_data_set(d, "one", color="red")
d2 = {2:1, 3:3, 4:8, 6:7, 7:9, 8:2, 9:1}
bgraph.add_data_set(d2, "two", color="blue")

bgraph.draw_graph("bar.png")

