@body
@h1 Checklist

This is my checklist:

- [] One
- [x]: text="Two" comments="This is completed" who="Brad" date="Nov 12, 2015"
    - [x]: text="This is some random item that wraps across lines" comments="Some info here" who="Brad"
    - [] B
    - [] C

These are some more items

#@checklist: style="table"
#--columns:
#    Item, Completed
#--items:
#- one, : caption="blah blah blah" checked="yes" who="Brad" date="Nov 12, 2015" comments="This task is completed"
#    - one.a, blah, blah, blah
#- two
#- three
#- four

@text
This is another checklist here that is a bit more sophisticated in
what it can display.

@checklist: title="test" caption="test" style="table"
- one: caption="blah blah blah" checked="yes"
- two
- three: checked="yes"
- four

@text
Here is something else

@checklist: style="table" column_splitter="|"
--name:
    This is my checklist
--columns:
    value | who | comments | status
--items:
- one   | belliott | I finished this task on Friday morning | closed
- two   | belliott | These are some comments here           | open
- three |          | These are some comments here           | pending
