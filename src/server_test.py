#!/usr/bin/env python
import xmlrpclib
import datetime
import base64

proxy = xmlrpclib.ServerProxy("http://127.0.0.1:8300")

contents = '''
@doctitle Blah blah
@docsubtitle TBD
@docversion 1.0
@body
@h1 This is a test
This is some more data

@h3 This is another header
Blah blah blah

@h4 Another heading
@table
- One | Two
- Three | Four
'''

settings = "html.header_numbers=0;html.inline_toc=0";

#print proxy.parse(contents, "html_inline", "unstyled", "")
#data = proxy.parse(contents, "pdf", "shorte", "")
data = proxy.parse(contents, "odt", "cortina_public", "")

if(data["type"] == "base64"):
    print base64.decodestring(data["content"])
else:
    print data["content"]


