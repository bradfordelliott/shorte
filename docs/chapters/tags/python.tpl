
@h3 @python
This tag is used to embed Python code directly into the document and
highlight it appropriately. If the code is a complete snippet it can
also be executed on the local machine and the results returned. See ExecutingSnippets
for more information on setting up Shorte to execute code snippets.

@shorte
\@python: exec="1"
print "Hello world!"

@text
This will execute the code on the local machine and return the output:

@python: exec="1"
print "Hello world!"
