import string
import sys

html = '''
<style>
table{border-collapse:collapse;width:600px;}
td{border:1px solid black;}
</style>
<table>
<tr style='background-color:#d0d0d0;font-weight:bold;'><td>Bit</td><td>Field</td><td colspan=2 style='border:0px;width:1px;background-color:white;'>&nbsp;</td><td>Bit</td><td>Field</td></tr>
'''

regs = []
regs.append({'width' : 8, 'name' : 'blah'})
regs.append({'width' : 2, 'name' : 'blah2'})
regs.append({'width' : 6, 'name' : 'blah3'})
regs.append({'width' : 16, 'name' : 'blah3'})

bit = 0
register_width = 32
col1 = []
col2 = []

bits = 0
for field in regs:
    bits += field["width"]
if(bits < register_width):
    regs.append({"width" : register_width - bits, 'name': 'reserved', 'type' : 'reserved'})

for field in regs:
    style=''
    if(field.has_key("type")):
        if(field["type"] == "reserved"):
            style="background-color:#ddd;"

    if(bit >= (register_width/2)):
        is_first = True
        for i in range(bit, bit+field["width"]):

            if(not is_first):
                if(not ('color:#bbb' in style)):
                    style += "color:#bbb;padding-left:10px;"
            is_first = False

            col2.append(string.Template(
                "<td $style>$bit</td><td $style>$name</td>").substitute(
                    {"bit" : bit, "name" : field["name"],
                     "style" : "style='%s'" % style}))
            bit += 1
    else:
        is_first = True
        for i in range(bit, bit+field["width"]):

            if(not is_first):
                if(not ('color:#bbb;' in style)):
                    style += "color:#bbb;padding-left:10px;"
            is_first = False

            col1.append(string.Template(
                "<td $style>$bit</td><td $style>$name</td>").substitute(
                    {"bit" : bit, "name" : field["name"],
                     "style" : "style='%s'" % style}))
            bit += 1

for i in range(0, len(col1)):
    html += "<tr>"
    html += col1[i]
    html += "<td colspan=2 style='border:0px;width:1px;background-color:white;'>&nbsp;</td>"
    html += col2[i]
    html += "</tr>"

html += "</table>"

print html
