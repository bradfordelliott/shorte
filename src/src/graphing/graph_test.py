#!/usr/bin/python
import sys
import re
import shutil
import os
sys.path.append('.')
sys.path.append('../..')
import libs.cairo_access
from libs.cairo_access import *
import math


import src.graphing.linegraph as linegraph
import src.graphing.bargraph as bargraph
import src.graphing.sequence_diagram as sequence_diagram
import src.graphing.timeline as timeline

lgraph = linegraph.line_graph_t(800,600)
lgraph.set_title("This is a test graph", "A test line graph with some data")
lgraph.set_xaxis("X-Axis", "red", 0, 10, 1)
lgraph.set_yaxis("Y-Axis", "red", 0, 10, 1)
    
d = {0:1, 1:3, 4:5, 6:4, 7:4, 8:3, 10:8}
lgraph.add_data_set(d, "one", color="red")

d2 = {2:1, 3:3, 4:8, 6:7, 7:9, 8:2, 10:1}
lgraph.add_data_set(d2, "two", color="blue")

lgraph.draw_graph("line.png")


bgraph = bargraph.bar_graph_t(1600,1200)
bgraph.set_title("This is a test graph", "A test bar graph with some data")
bgraph.set_xaxis("X-Axis", "red", 0, 10, 1)
bgraph.set_yaxis("Y-Axis", "red", 0, 10, 1)
    
d = {0:1, 1:3, 4:5, 6:4, 7:4, 8:3, 9:8}
bgraph.add_data_set(d, "one", color="red")
d2 = {2:1, 3:3, 4:8, 6:7, 7:9, 8:2, 9:1}
bgraph.add_data_set(d2, "two", color="blue")

bgraph.draw_graph("bar.png")

events = []
title = "test"
desc = "test"
imagemap = "test"
output = "test.svg"

event = {}
event["type"] = "message"
event["from"] = "a"
event["to"] = "b"
event["name"] = "one"
event["desc"] = "Test"
events.append(event)

event = {}
event["type"] = "message"
event["from"] = "b"
event["to"] = "a"
event["name"] = "two"
event["desc"] = "test"
events.append(event)

event = {}
event["type"] = "message"
event["from"] = "b"
event["to"] = "c"
event["name"] = "three"
event["desc"] = "test"
events.append(event)

event = {}
event["type"] = "message"
event["from"] = "c"
event["to"] = "d"
event["name"] = "four"
event["desc"] = "test"
events.append(event)

(output_file, imagemap, events) = sequence_diagram.generate_diagram(events=events,
    title=title, description=desc,
    target_width=1600,
    target_height=1200,
    #imagemap_name="test",
    base_file_name="test2")


shutil.copyfile(output_file, os.path.basename(output_file))


# Create a Timeline Graph
timeline = timeline.timeline_graph_t(800, 400)
timeline.set_title("This is a test graph", "A test timeline with some data")
timeline.set_xaxis("Time", "red")
timeline.set_yaxis("Y-Axis", "red")
    
#d = {0:5, 1:20, 6:35, 4:55, 7:22, 11:100}
#timeline.add_data_set(d, "one", color="c0c0c0")
    
d = {0:5, 1:20, 6:35, 4:55, 12:10, 14:10}
timeline.add_data_set(d, "one", color="c0c0c0")

d2 = {1:6, 7:15, 15:40}
timeline.add_data_set(d2, "two", color="f00000")

d3 = {9:20, 10:30}
timeline.add_data_set(d3, "three", color="0000f0")

timeline.draw_graph("timeline.png")
