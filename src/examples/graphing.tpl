@doctitle Plots and Graphs
@docsubtitle Some Random Graphs
@body

@h1 Line Graphs

This is an example of a line graph.
@graph: type="line" width=600 height=400 title="Blah blah blah" subtitle="Subtitle" bgcolor="#ffffff" frame=True filled=False
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

@text
Another example of a graph with negative numbers
@graph: type="line" width=600 height=400 title="Blah blah blah" subtitle="Subtitle" bgcolor="#ffffff" frame=True filled=False
--data:
data = {}
data["one"] = {
    -1:10,
    0: 1,
    1: 3,
    4: -5,
    6: 4,
    7: -4,
    8: 3,
    10: 8,
    5.6: 7,
}

@text
This is a randomly generated line graph
@graph: type="line" width=800 height=600 title="A random line graph" subtitle="Randomly generated" bgcolor="#b0b0b0" filled=True
--data:
<?
import math
import random
result = '''
data={}
data["one"] = {}
data["two"] = {}
'''

points = random.randint(5,10)
x = 0
for i in range(0, points):
    x += random.randint(2,100)
    y = random.randint(2, 100)
    result += 'data["one"][%d] = %f\n' % (x, y)

x = 0
for i in range(0, points):
    x += random.randint(2,100)
    y = random.randint(2, 100)
    result += 'data["two"][%d] = %f\n' % (x, y)

?>

@text
A few randomly generated graphs
<?
import random
result = ''
for i in range(0, 10):
    result += '''@graph: type='line'
--data:
data = {}
data["one"] = {}
data["two"] = {}
'''
    yrange = random.randint(100, 1000)
    x = 0
    for j in range(2, 10):
        x += random.randint(2,100)
        y = random.randint(2, yrange)
        result += 'data["one"][%d] = %f\n' % (x,y)
        
    x = 0
    for j in range(2,20):
        x += random.randint(2,100)
        y = random.randint(2, yrange)
        result += 'data["two"][%d] = %f\n' % (x,y)
?>



@h1 Pie Graphs
This is an example of a pie graph
@graph: type="pie" title="A Pie Graph" width=600 height=400 subtitle="Just a random pie graph" bgcolor="#a0a0a0"
--data:
data = {}
data["one"] = {
    "A": 1,
    "B": 10,
    "C": 50.5,
    "D": 20.2
}

data["two"] = {
    "E" : 20,
    "F" : 30
}

@text
This is a randomly generated pie graph

@graph: type="pie" title="A random pie graph" width=800 height=600 subtitle="A randomly generated piegraph"
--data:
<?
import math
import random
result = '''
data={}
data["one"] = {}
data["two"] = {}
'''

points = random.randint(5,10)
for i in range(0, points):
    result += 'data["one"]["%d"] = %f\n' % (i, random.randint(2, 10))

points = random.randint(5,10)
for i in range(0, points):
    result += 'data["two"]["%d"] = %f\n' % (i, random.randint(2, 10))
?>

@h1 Bar Graphs
This is an example of a bar graph.
@graph: type="bar" title="A Bar Graph" subtitle="Just a random graph"
--data:
data = {}
data["one"] = {
    0:  1,
    1:  3,
    4:  -5,
    6:  4,
    7:  -4,
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

@graph: type="line" title="A generated graph" caption="This is a random caption"
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


@h1 A Memory Map Graph
@graph: type="memorymap" title="A memory map graph"
--data:
<?
result = '''
data = {}
data["DRAM"] = {"start" : 0x5ffc0000, "end" : 0x5ffc7fff}
data["IROM"] = {"start" : 0x5ffe0000, "end" : 0x5ffe1fff}
data["IRAM"] = {"start" : 0x5fff0000, "end" : 0x5fff7fff}
'''
?>

@h1 A Timeline
This is an example of a timeline plot

@graph: type="timeline" title="A generated timeline"
--data:
<?
result = '''
base = 0
data = {}
data["one"] = {
    1977 - base: {"val" : 5,   "label" : "Test 0",  "caption" : "Test 1"},
    1978 - base: {"val" : 20,  "label" : "Test 1",  "caption" : "Test 2"},
    1979 - base: {"val" : 35,  "label" : "Test 6",  "caption" : "Test 3"},
    1989 - base: {"val" : 55,  "label" : "Test 4",  "caption" : "Test 4"},
    1993 - base: {"val" : 100, "label" : "Test 12", "caption" : "Test 5"},
    1999 - base: {"val" : 10,  "label" : "Test 14", "caption" : "Test 6"},
    2001 - base: {"val" : 100, "label" : "Test 15", "caption" : "Test 7"}
}
'''
?>

@h1 A Sequence Diagram
@sequence: title="Ethernet KR"
- Type    | Source         | Sink           | Name                           | Description
- action  | API            |                | Initialization                 | The API starts initializing the ASIC, the microsequencer is currently stalled 
- message | API            | Microsequencer | SPARE1[0] == 1, SPARE1[4] == 1 | The API starts AN by setting SPARE1[0] == 1. It also asserts SPARE1[4]
                                                                               as a stop indicator to the microcode.
- loop    | API            |                | Wait for SPARE20 == 1          | The API then busy waits for AN completion by polling for SPARE20 == 1
- message | Microsequencer | AN             | Start AN                       | The microsequencer tells the AN hardware to start the negotiation
                                                                               process.
- message | AN             | Link Partner   | DME Pages                      | The AN hardware starts exchanging DME pages with the link partner
- message | Link Partner   | AN             | DME Pages                      | DME pages are exchanged to negotiate the link protocol.
- message | AN             | Microsequencer | AN Complete                    | The AN hardware indicates completion.
- message | Microsequencer | API            | Assert SPARE20 == 1            | The microsequencer asserts SPARE20 == 1 to indicate AN completion
- action  | API            |                | Host configuration             | The API proceeds to configure the host interface based
                                                                               on the negotiated results.

