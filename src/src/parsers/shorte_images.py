import string
import os
from src.shorte_defines import *

try:
    from PIL import Image
except:
    WARNING("Failed to load Image library. Try installing it using the command 'pip install Pillow'")

class image_t:
    def __init__(self):
        self.caption = ""
        self.source = ""
        self.height = 0
        self.width = 0
        self.name = ""
        self.extension = ""
        self.thumb_height = 0
        self.thumb_width = 0

    def __str__(self):
        output = string.Template('''
image_t:
  name:         ${name}
  source:       ${source}
  caption:      ${caption}
  height:       ${height}
  width:        ${width}
  thumbnail:    ${thumb}
  thumb.width:  ${thumb_width}
  thumb.height: ${thumb_height}
''').substitute({
    "name" : self.name,
    "source" : self.source,
    "caption" : self.caption.strip(),
    "height"  : self.height,
    "width"   : self.width,
    "thumb"   : self.get_thumbnail(),
    "thumb_height" : self.thumb_height,
    "thumb_width"  : self.thumb_width})
        return output



    def parse_path(self, path):
        self.source = os.path.abspath(path)
        dirname = os.path.dirname(path) + os.path.sep
        name = path.replace(dirname, "")
        parts = os.path.split(name)
        self.name = name
        self.dirname = dirname

        parts = os.path.splitext(parts[1])
        self.basename = parts[0]
        self.extension = parts[1]

    def get_name(self):
        return self.basename + self.extension

        #print "BASENAME: %s" % self.basename
        #print "DIRNAME:  %s" % dirname

    def get_caption(self):
        return self.caption

    def dimensions(self):

        if(self.height == 0 or self.width == 0):
            im = Image.open(image.source)
            self.width = im.size[0]
            self.height = im.size[1]
        
        return (self.width, self.height)

    def to_dict(self):
        image = {}
        image["name"] = self.name
        image["ext"] = self.extension
        image["src"] = self.soure
        image["height"] = self.height
        image["width"] = self.width
        image["caption"] = self.caption
        image["center"] = False
        image["href"] = None
        image["align"] = ""
        image["imagemap"] = None
        image["reference"] = None

        return image
    
    def scale(self, new_height=None, new_width=None):
        width = 0
        height = 0

        width_scale_percentage  = False
        height_scale_percentage = False
        
        im = Image.open(self.source)
        
        #print ("1: New height: ", new_height)
        #print ("1: New width:  ", new_width)
        #print ("1: im[0] (width):  ", im.size[0])
        #print ("1: im[1] (height): ", im.size[1])

        if(new_height == None):
            new_height = (new_width / (1.0 * im.size[0])) * im.size[1]
        if(new_width == None):
            new_width = (new_height / (1.0 * im.size[1])) * im.size[0]
        

        new_height = int(new_height)
        new_width = int(new_width)

        if(new_height > im.size[1]):
            new_height = im.size[1]
            new_width  = im.size[0]
        if(new_width > im.size[0]):
            new_height = im.size[1]
            new_width  = im.size[0]
        
        #print ("2: old.height: %d, new.height: %d" % (im.size[1], new_height))
        #print ("2: old.width:  %d, new.width:  %d" % (im.size[0], new_width))

        width = new_width
        height = new_height


        #width = new_width
        #if(not isinstance(new_width, (int,long))):
        #    if("%" in new_width):
        #        width_scale_percentage = True
        #        width = re.sub("%", "", new_width)
        #    elif("px" in new_width):
        #        width = re.sub("px", "", new_width)
        #    width = int(width)

        #height = new_height
        #if(not isinstance(new_height, (int,long))):
        #    if("%" in new_height):
        #        height_scale_percentage = True
        #        height = re.sub("%", "", height)
        #    elif("px" in new_height):
        #        height = re.sub("px", "", height)
        #    height = int(height)

        #if(width_scale_percentage or height_scale_percentage):
        #    ERROR("Can't scale images by percentage yet")
        #    return self.name

        ##print "SOURCE: %s" % self.source

        #scale_width  = 1.0
        #scale_height = 1.0
        #if(width > 0):
        #    scale_width = (width / (im.size[0] * (1.0)))
        #    if(height == 0):
        #        scale_height = scale_width

        #if(height > 0):
        #    scale_height = (width / (im.size[1] * (1.0)))
        #    if(width == 0):
        #        scale_width = scale_height

        #width  = scale_width * im.size[0]
        #height = scale_height * im.size[1]
        
        #print "1: WIDTH: %d, HEIGHT: %f" % (width,height) 

        # DEBUG BRAD: Resize the image to fit
        im = im.resize((int(width),int(height)), Image.BICUBIC)
        scratchdir = shorte_get_config("shorte", "scratchdir")
        name = self.basename + "_%dx%d" % (width,height)
        img = scratchdir + os.path.sep + name + self.extension
        im.save(img)

        return (img, int(height), int(width))

    def create_thumbnail(self,height=200,width=200):
        #print "Creating thumbnail"
        #if(height):
        #    print "  height=%d" % height
        #if(width):
        #    print "  width=%d" % width
        (img, height, width) = self.scale(new_height=height, new_width=width)

        self.thumb_height = height
        self.thumb_width = width

        return img

    def get_thumbnail(self):
        #print "Creating thumbnail"
        return self.basename + "_%dx%d" % (self.thumb_width, self.thumb_height) + self.extension

    def get_thumb_width(self):
        return self.thumb_width

    def get_thumb_height(self):
        return self.thumb_height

    def __str__(self):
        output =  "image_t\n"
        output += "=======\n"
        output += "  caption   = %s\n" % self.caption
        output += "  name      = %s\n" % self.name
        output += "  extension = %s\n" % self.extension
        return output
        


class gallery_t:
    def __init__(self):
        self.m_images = []
        pass

    def add_image(self, image):
        self.m_images.append(image)

    def images(self):
        return self.m_images
