@h2 Images and Image Maps
@h3 @image
The @image tag is used to include an image. Recommended image formats
currently included .jpg or .png. The image tag takes the
following format

@shorte: exec=True
\@image: src="chapters/images/shorte.png" caption="The shorte logo" width="100px"

@text
You can also scale images. The following example shows the image scaled to 50% of it's actual width:

@shorte: exec=True
\@image: src="chapters/images/shorte.png" caption="The shorte logo" width="50%"

@h3 @imagemap
This tag is used to generate an Image map. It currently only works in the
HTML output template. Links are not currently supported.

@shorte
\@imagemap: title="one"
- shape  | coords         | Label       | Description
- circle | 50,50,50       | A Circle    | This is a description of my circle
- rect   | 72,144,215,216 | A rectangle | This is a description of my rectangle.

\@image: map="one" src="chapters/images/imagemap.png"

@text
Will generate the following imagemap:

@imagemap: title="one"
- shape  | coords         | Label       | Description
- circle | 50,50,50       | A Circle    | This is a description of my circle
- rect   | 72,144,215,216 | A rectangle | This is a description of my rectangle.

@image: map="one" src="chapters/images/imagemap.png"
