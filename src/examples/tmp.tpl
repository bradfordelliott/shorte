# This is a comment

@body This is a test

@h1 This is a test

<?
result = '''
@h2 '''
if(exists('SKU')):
    if(SKU == "CS4321"):
        result += "Cortina Systems CS4321 Quad XFI with Security/SFP+"
    else:
        result += "TBD"
else:
    result += "SKU not defined"


result += '''
@text
'''
for i in range(0, 20):
    result += "blah blah blah\n\n"
?>

@questions
Q: This is a test
A: This is an answer
Q: This is a another question
Q: This is a third question

@text: if="(not CUG) or PUG"
This is some *bold* text

@table
- Heading 1 | Heading 2
- Val 1     | Val 2
- Val 3     | Val 4

@ol
- One
    - Two
        - Three
    - Four
    - Five
- Two
- Three
    - Four

