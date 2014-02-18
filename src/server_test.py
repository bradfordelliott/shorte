#!/usr/bin/env python
import xmlrpclib
import datetime
import base64
from optparse import OptionParser


contents = '''
@doctitle Blah blah
@docsubtitle TBD
@docversion 1.0
@body
@h1 This is a test
This is some more data

@h3 This is another header
Blah blah blah

@h3: skip_if_pdf
This is another header
Blah blah blah

@h4 Another heading
@table
- One | Two
- Three | Four
'''

parser = OptionParser()
parser.add_option("-p", "--package",
                  action="store", dest="package",
                  help="The test document to generate")
parser.add_option("-t", "--theme",
                  action="store", dest="theme",
                  help="The theme to use")
parser.add_option("-s", "--shutdown",
                  action="store_true", dest="shutdown",
                  help="Shutdown the server")
parser.add_option("-z", "--zip",
                  action="store_true", dest="zip", default="",
                  help="Zip the output")
parser.add_option("--ip", "--ip",
                  action="store", dest="ip", default="127.0.0.1",
                  help="The IP address to connect to")
parser.add_option("--port", "--port",
                  action="store", dest="port", default="8300",
                  help="The port to connect to")

(options, args) = parser.parse_args()

addr = "http://%s:%d" % (options.ip, int(options.port))
print "Connecting to %s" % addr
proxy = xmlrpclib.ServerProxy(addr)

if(options.shutdown):
    import sys
    proxy.shutdown()
    sys.exit(0)


settings = "html.header_numbers=0;html.inline_toc=0";

#print "package: %s" % options.package
#print "theme: %s" % options.theme

data = proxy.parse(contents, options.package, options.theme, settings, options.zip)

if(data["type"] == "base64"):
    print base64.decodestring(data["content"])
elif(data["type"] == "zip"):
    print base64.decodestring(data["content"])
else:
    print data["content"]



