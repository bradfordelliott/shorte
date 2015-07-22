@doctitle Shorte
@docsubtitle Cairo Examples
@body
@h1 Cairo Examples

#@image: src="examples/gallery/one.jpg"

This is an example image:

@python: exec=True save_image='cairo.png' path_add_shorte=True
#0         1         2         3         4         5         6         7
#01234567890123456789012345678901234567890123456789012345678901234567890123456789
from src.graphing.graph import *

cairo = cairo_t(10, 10)

# Draw a background
cairo.draw_rect(x=0, y=0,
                width=300, height=300,
                background_color='#ffffff', line_color='#000000', line_width=0.9)

# Draw a rounded rectangle
cairo.draw_rounded_rect(x=100, y=100,
    width=250, height=250, radius=10,
    background_color='#c0c0c0', line_color='#000000', line_width=0.9)

# Save as PNG
print "Saving cairo.png"
cairo.write_to_png("cairo.png", 300, 300)


@python: exec=True save_image='cairo.png' path_add_shorte=True
from src.graphing.graph import *

cairo = cairo_t(300, 300)

# Draw the background
cairo.draw_rect(x=0, y=0,
    width=300, height=300,
    background_color='#ffffff', line_color='#000000', line_width=0.9)

# Draw a rounded rectangle
cairo.draw_rounded_rect(x=100, y=100,
    width=250, height=250, radius=10,
    background_color='#ff0000', line_color='#000000', line_width=0.9)

# Save as PNG
cairo.write_to_png("cairo.png", 300, 300)

@python: exec=True save_image='blah.png'
import cairo

surface = cairo.ImageSurface.create_from_png("examples/test.png")
ctx = cairo.Context(surface)

ctx.scale(0.5, 0.5)

surface.write_to_png("blah.png")

#cairo.write_to_png("blah.png")
#cairo.set_source_surface(im, 10, 10)

#cairo.paint()
