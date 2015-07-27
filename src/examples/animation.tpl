@body
@h1 An Animation
@text
This is a randomly generated line graph. We're hiding all the
generated tags since we don't want to see them.

<?
import random
output = ''
data = []

for i in range(0, 40):
    x = i
    y = random.randint(1,40)
    data.append((x,y))
    
    output += '''
@graph: type='line' width=600 height=400 visible=False max_x=40 max_y=40
--data:
data = {}
data["graph"] = {}
'''

    for j in range(0, len(data)):
        output += '''
data['graph'][%d] = %f
''' % (data[j][0], data[j][1])
    
#    output += '''
#@pre
#'''
#    for j in range(0, len(data)):
#        output += '''
#data['graph'][%d] = %f
#''' % (data[j][0], data[j][1])

result = output
?>

@perl: exec=True visible=True
`rm -rf scratch/output.gif`;
`convert -delay 5 -loop 0 -dither None -colors 80 "scratch/graph_*.png" "scratch/output.gif"`;

@text
This will generate the following images:
@image: src="scratch/output.gif"

