#!/usr/bin/env python
import os
from PIL import Image

def make_contact_sheet2(fnames):
    
    width = 1024
    
    dimensions = []
    for f in fnames:
        img = Image.open(f)
        w = img.size[0]
        h = img.size[1]

        print "%d x %d" % (w,h)

        nh = 400
        nw = w * int(nh / (h * (1.0)))

        print "Resizing to %d x %d" % (nw,nh)

        #img = img.resize(nw, nh)
        

def make_contact_sheet(fnames,(ncols,nrows),(photow,photoh),
                       (marl,mart,marr,marb),
                       padding):
    """\
    Make a contact sheet from a group of filenames:

    fnames       A list of names of the image files
    
    ncols        Number of columns in the contact sheet
    nrows        Number of rows in the contact sheet
    photow       The width of the photo thumbs in pixels
    photoh       The height of the photo thumbs in pixels

    marl         The left margin in pixels
    mart         The top margin in pixels
    marr         The right margin in pixels
    marb         The bottom margin in pixels

    padding      The padding between images in pixels

    returns a PIL image object.
    """

    # Calculate the size of the output image, based on the
    #  photo thumb sizes, margins, and padding
    marw = marl+marr
    marh = mart+ marb

    padw = (ncols-1)*padding
    padh = (nrows-1)*padding
    isize = (ncols*photow+marw+padw,nrows*photoh+marh+padh)

    # Create the new image. The background doesn't have to be white
    white = (255,255,255)
    inew = Image.new('RGB',isize,white)

    count = 0
    # Insert each thumb:
    for irow in range(nrows):
        for icol in range(ncols):
            left = marl + icol*(photow+padding)
            right = left + photow
            upper = mart + irow*(photoh+padding)
            lower = upper + photoh
            bbox = (left,upper,right,lower)
            try:
                # Read in an image and resize appropriately
                img = Image.open(fnames[count]).resize((photow,photoh))
            except:
                break
            inew.paste(img,bbox)
            count += 1
    return inew

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-p", "--path",
                  action="store", dest="path",
                  help="The path where the files exist")
parser.add_option("-o", "--output",
                  action="store", dest="output",
                  help="The path to save the output to")

(options, args) = parser.parse_args()

fnames = []
for root, dirs, paths in os.walk(options.path):
    for path in paths:
        (base, ext) = os.path.splitext(path)
        if(ext == ".jpg"):
            fnames.append(root + "/" + path)

image = make_contact_sheet(fnames, (4,4), (300,400), (10,10,10,10), 10)
image.save("contact.jpg")

make_contact_sheet2(fnames)
