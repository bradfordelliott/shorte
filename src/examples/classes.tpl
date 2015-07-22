@doctitle Classes
@docsubtitle Shorte Examples

@body

@h1 my_class
This example file attempts to demonstrate how shorte manages class objects.

@class
-- name: my_class
-- extends: my_base_class
-- description:
    This is a description of my class here
-- public.functions:
    -- my_class
    -- method1
-- public.members:
    -- enum1 a
    -- string b
-- properties:
    -- x
    -- y
#-- private.functions:
#    -- xxx
#-- private.members:
#    -- int a
#    -- int b

@h4 enum1
@enum
--name: enum1
--values:
    - one | 1 | TBD
    - two | 2 | TBD

@h4 my_class
@prototype
-- name: my_class
-- class: my_class
-- prototype:
    my_class(int param1);
-- description:
    Constructor for the my_class object

@h4 method1
@prototype
-- name: method1
-- class: my_class
-- prototype:
    int method1(int param1);
-- description:
    A description of this class method
--deprecated:
    This method is no longer used.
--example:
    method1(p1);
--see:
    xxx
--since:
    Version 1.0

@h4 xxx
@prototype: private=True
-- name: xxx
-- class: my_class
-- prototype:
    int xxx(int v)
-- description:
    This is a description
--private:
    True
