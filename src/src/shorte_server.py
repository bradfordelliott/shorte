
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

from src.shorte_defines import *
from src.shorte_engine import *

# Restrict to a particular path
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


def parse(contents, theme):
     
    return 0xdead

def shorte_server_start(ip, port):

    print "Starting the shorte XML-RPC server on %s:%d" % (ip,port)
    # Create the server
    server = SimpleXMLRPCServer((ip, port), requestHandler=RequestHandler)
    server.register_introspection_functions()

    config = shorte_get_startup_path() + os.path.sep + "shorte.cfg"
    output_dir = "build-output"
    parser = "shorte"
    shorte = engine_t(output_dir, config, parser)

    # Register a test function
    server.register_function(parse)
    
    server.serve_forever()
