@doctitle This is a test
@docsubtitle This is a subtitle
@docauthor Brad Elliott
@docversion 1.0

@body
@h1 The first heading
- This is a test
   - Two

This is some more text with an inline table
@{table,
- One | Two
- Three | Four
}

and now some more stuff with some @{b, bold} text.

@c
int main(void)
{
    printf("Hello world!");
}

@python
print "Hello world!"

@h1 Slide 2
Some random text here

A new paragraph

@table
- One   | Two
- Three | Four is a column with some really long
          text that wraps around to a newline. I wonder
          how shorte will handle this???
- Five  | Six

@text
This is another paragraph in this slide


@h1 Slide 3
@h2 Level 2
Blah blah blah

@h3 Level 3

@note
This is a test

@warning
This is something to be careful about!!! It contains some really long
text with a new paragraph

like this and then a list
- one
    - two
    - three

and even a table
@{table,
- One | Two
- Three | Four
}

@note
This is a test

@h1 Slide 4
@image: src="examples/record_0.png"

@h1 Slide 5
This is an ordered list
@ol
- One
- Two
    - Three
        - Four
            - Five
-

@text
This is an unordered list
- One
- Two
    - Three
        - Four
    - Five
- Six
