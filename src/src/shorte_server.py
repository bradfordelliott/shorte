#!/usr/bin/env python
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import shutil
import os

from src.shorte_defines import *
from src.shorte_engine import *

g_shorte = None
g_server = None

class shorte_server_t(SimpleXMLRPCServer):
    def serve_forever(self):
        self.quit = 0
        while not self.quit:
            self.handle_request()

# Restrict to a particular path
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

def shutdown():
    global g_server
    print "Received shutdown message"
    g_server.quit = 1
    return 1

def parse(contents, package, theme, settings, zip_output):
    global g_shorte

    #print "Theme: %s" % theme
    #print "Package: %s" % package

    config = shorte_get_startup_path() + os.path.sep + "shorte.cfg"
    output_dir = "scratch2"
    if(not os.path.isabs(output_dir)):
        output_dir = "%s/%s" % (os.getcwd(), output_dir)
    try:
        shutil.rmtree(output_dir, True)
    except:
        pass

    os.makedirs(output_dir)
    parser = "shorte"

    if(settings != None):
        settings = settings.split(";")

        for s in settings:
            matches = re.search("(.*?)\.(.*?)=(.*)", s)

            if(matches != None):
                sect = matches.groups()[0]
                key = matches.groups()[1]
                val = matches.groups()[2]
               
                g_shorte.set_config(sect, key, val)

    try:
        g_shorte.set_output_directory(output_dir)
        g_shorte.parse_string(contents)
        
        g_shorte.set_package(package)

        info = {}

        if(zip_output != ""):
            g_shorte.generate_packages(package, theme, None, "test.zip")

            info["type"] = "zip"
            content = "TBD"
            handle = open("test.zip", "rb")
            content = handle.read()
            handle.close()
            content = base64.encodestring(content)
        else:
            indexer = indexer_t()

            if(package == "html_inline"):
                info["type"] = "text"
                g_shorte.set_theme(theme)
                template = template_html_t(g_shorte, indexer)
                template.m_inline = True
                template.set_template_dir(package)
                g_shorte.set_template(template)
                template.m_include_pdf = False
                content = g_shorte.generate_string(package)
            elif(package in ("odt","pdf")):
                info["type"] = "base64"
                g_shorte.set_theme(theme)
                template = template_odt_t(g_shorte, indexer)
                g_shorte.set_template(template)
                content = g_shorte.generate_string(package)
            else:
                info["type"] = "text"
                content = "???"

    except Exception as e:
        content = "Caught an exception parsing the input"
        ERROR("Caught an exception parsing the input")
        content = e.__str__()

    # Reset the engine to process the next request
    g_shorte.reset()

    #if(package in ("odt","pdf")):
    #    info["type"] = "base64"
    #elif(package in ("html_inline+pdf")):
    #    info["type"] = "zip"
    #    content = "TBD"
    #    handle = open("test.zip", "rb")
    #    content = handle.read()
    #    handle.close()
    #    content = base64.encodestring(content)

    info["content"] = content
    return info


def shorte_server_start(ip, port):
    global g_shorte
    global g_server

    print "Starting the shorte XML-RPC server on %s:%d" % (ip,port)
    # Create the server
    g_server = shorte_server_t((ip, port), requestHandler=RequestHandler)
    g_server.register_introspection_functions()
    g_server.register_function(shutdown)

    config = shorte_get_startup_path() + os.path.sep + "shorte.cfg"
    output_dir = "build-output"
    if(not os.path.isabs(output_dir)):
        output_dir = "%s/%s" % (os.getcwd(), output_dir)
    parser = "shorte"
    g_shorte = engine_t(output_dir, config, parser)

    # Register a test function
    g_server.register_function(parse)
    
    g_server.serve_forever()
