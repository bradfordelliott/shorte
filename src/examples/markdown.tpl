@doctitle Markdown Support
@docsubtitle Support for Markdown

@body

@h1 Markdown
The following provides a demonstration of markdown
support in textblocks.

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
>   Some indented text in the block quote
>   
>   and another indented paragraph
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
    2. More Stuff

```python
This should be some code but I don't support the language
type yet.
```

> This is some quoted code:
> ```c
> This is some quoted code here
> ```

\# THis is a level 1 heading

@h1 Another heading

#@h2 Another paragraph
#@text
#This is a
#> This is a block quote.
#>  
#> This is another line in a block quote with
#> a nested list:
#> - one
#>     - two
#> - three
#
#@quote
#This is a random quote from some person


#@markdown
#Heading 1
#=========
#> This is a block quote
#> This is a second line
#> This is another block quote

