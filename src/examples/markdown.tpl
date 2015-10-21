@doctitle Markdown Support
@docsubtitle Support for Markdown

@body
@h1 Markdown

The following provides a `demonstration` of markdown
support in textblocks. It @{bold,includes} support for @{italic,markdown tags}.
This line should wrap across multiple lines if I've done
things correctly. However, my @{hl,inline code block} shouldn't
make things look wonky and @{pre,shouldn't} overlap the next line.

    This is a block of indented text
     
    and a new paragraph

    This block is doubly nested
    with a second line that shouldn't wrap
    because I want to treat it like a block of code

    This block is triply nested
    and it shouldn't wrap

@{pre,
This is a block of code
}

I'd like to be able to have blocks of code inside list items. Right
now I can only do that with inline tags but that doesn't work very
well inside PDFs.

- one
  - two
      @{code,
blah blah blah
blah blah blah
      }
  - three
    - a
    - b
      @{code,
This is some more nested code
inside a list item.
}
- four

@markdown
This is an image: ![Image of Yaktocat](https://octodex.github.com/images/yaktocat.png)

Change the definition of the primary network interface eth0 to look like the following. Use your assigned network values in place of the 10.243.10.x values.

    # The primary network interface
    auto eth0
    iface eth0 inet static
        address 10.243.10.5
        netmask 255.255.255.0
        gateway 10.243.10.1
    
    This should be a new paragraph
    and this should be part of the same paragraph

@text
This is a link to a URL http://www.cbcnews.ca/news/blah
and some more stuff here. I could also have
an ftp://www.cbc.ca link. What happens with a link
to an internal site like http://sw/jenkins

This is a markdown style link to [CBC](http://www.cbc.ca).

This is a shorte format link [[http://www.cbc.ca,to cbc.ca]]



@markdown
This is a block of markdown text

> A quote
> > A nested quote

# A markdown header
Some other random text

## A second level header
With some text right after it

A horizontal rule

===

Markdown H1
===========

Markdown H2
-----------

This is a link to a URL http://www.cbcnews.ca/news/blah
and some more stuff here. I could also have
an ftp://www.cbc.ca link. What happens with a link
to an internal site like http://sw/jenkins

This is a markdown style link to [www.cbc.ca](http://www.cbc.ca).

This is a shorte format link [[http://www.cbc.ca,to cbc.ca]]

@text
This is a new textblock

@text
This is a textblock with an inline quote

@{quote,
This is my inline quote
}
     
This is another line in a block quote with
a nested list:

    This is indented text

        This is indented deeper

            as is this paragraph

> THis is a block quote
> and more data in the block quote
>   
>     Some indented text in the block quote
>     
>     and another indented paragraph
>
> What happens with a quote within a quote?
> > This is a nested quote
> >  
> > This is another paragraph in a nested quote
> > > This is triple nested
> 
> This is a list within a block quote
> - one
>   - two
>     - three
>

Finally we have a list:
- One
  - Two
    - Three

- A numbered list

I should be able to have an ordered list:

1. One
2. Two
3. Three
    1. Stuff
        1. ABC
        2. DEF
    2. More Stuff
        3. XYZ

```python
This should be some code but I don't support the language
type yet.
```

> This is some quoted code:
> ```c
> This is some quoted code here
> ```
> > This is a doubly nested quoted code block
> > ```javascript
> > alert("Hello world!")
> > ```
> And now back to our regularly scheduled input

@h1 This is a Random Heading

@markdown
This is a block of markdown text.

@h2 Another paragraph
@text
This is a
> This is a block quote.
>  
> This is another line in a block quote with
> a nested list:
> - one
>     - two
> - three

@quote
This is a random quote from some person


@markdown
# Heading 1
> This should be a block quote but it appears the markdown parser doesn't parse it properly.
> 
> This is a second paragraph
> 
> This is another block quote

# A heading with some markdown in it.
Some random data
> A block quote
> > A nested block quote
Another paragraph
- One
  - Two
    - Three
  - Four
- Two
  - Three

@include "examples/example.markdown"
