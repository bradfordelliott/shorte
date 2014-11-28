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
-- members:
    -- my_class

@prototype
-- name: my_class
-- class: my_class
-- prototype:
    my_class::my_class(int param1);
-- description:
    Constructor for the my_class object

@prototype
-- name: method1
-- class: my_class
-- prototype:
    int method1(int param1);
-- description:
    A description of this class method
