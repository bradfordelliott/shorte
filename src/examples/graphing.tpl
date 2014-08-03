@body

@h1 Line Graphs
This is an example of a line graph.
@graph: type="line" width=600 height=400 title="Blah blah blah" subtitle="Subtitle"
--data:
data = {}
data["one"] = {
    0: 1,
    1: 3,
    4: 5,
    6: 4,
    7: 4,
    8: 3,
    10: 8
}

data["two"] = {
    0:  10 + 1,
    1:  10 + 3,
    4:  10 + 5,
    6:  10 + 4,
    7:  10 + 4,
    8:  10 + 3,
    10: 10 + 8
}

@h1 Bar Graphs
This is an example of a bar graph.
@graph: type="bar" title="A Bar Graph" subtitle="Just a random graph"
--data:
data = {}
data["one"] = {
    0:  1,
    1:  3,
    4:  5,
    6:  4,
    7:  4,
    8:  3,
    11: 8,
    22: 9,
    25: 11
}
data["two"] = {
    0: 1,
    1: 8,
    4: 9,
    6: 3,
    7: 12,
    8: 7
}

@h1 A Generated Line Graph
This plot is an example of a generated graph using embedded
Python.

@graph: type="line" title="A generated graph"
--data:
<?
import math
result = '''
data={}
data["line"] = {}
'''
for i in range(0, 10):
    result += 'data["line"][%d] = %d\n' % (i, i)

# Now generate a sine wave
result += '''
data["sine"] = {}
'''
for i in range(0, 10):
    result += 'data["sine"][%f] = %f\n' % (i, 3 + math.sin(i))
?>
