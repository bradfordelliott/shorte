
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

from src.shorte_defines import *
from src.shorte_engine import *

g_shorte = None 

# Restrict to a particular path
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


def parse(contents, theme, settings):
    global g_shorte
    
    config = shorte_get_startup_path() + os.path.sep + "shorte.cfg"
    output_dir = "build-output"
    parser = "shorte"
    #g_shorte = engine_t(output_dir, config, parser)
    g_shorte.set_theme(theme)

    if(settings != None):
        settings = settings.split(";")

        for s in settings:
            matches = re.search("(.*?)\.(.*?)=(.*)", s)

            if(matches != None):
                sect = matches.groups()[0]
                key = matches.groups()[1]
                val = matches.groups()[2]
               
                g_shorte.set_config(sect, key, val)

    g_shorte.parse_string(contents)
    
    g_shorte.set_package('html_inline')

    indexer = indexer_t()
    
    template = template_html_t(g_shorte, indexer)
    template.m_inline = True
    template.set_template_dir('html_inline')
    template.m_include_pdf = False

    g_shorte.set_template(template)
    content = g_shorte.generate_string('html_inline')

    g_shorte.reset()

    return content


def shorte_server_start(ip, port):
    global g_shorte

    print "Starting the shorte XML-RPC server on %s:%d" % (ip,port)
    # Create the server
    server = SimpleXMLRPCServer((ip, port), requestHandler=RequestHandler)
    server.register_introspection_functions()

    config = shorte_get_startup_path() + os.path.sep + "shorte.cfg"
    output_dir = "build-output"
    parser = "shorte"
    g_shorte = engine_t(output_dir, config, parser)

    # Register a test function
    server.register_function(parse)
    
    server.serve_forever()
