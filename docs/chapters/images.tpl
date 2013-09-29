@h2 Images and Image Maps
@h3 @image
The @image tag is used to include an image. Recommended image formats
currently included .jpg or .png.

@h3 @imagemap
This tag is used to generate an Image map. It currently only works in the
HTML output template. Links are not currently supported.

@shorte
\@imagemap: id="one"
- shape  | coords         | Label       | Description
- circle | 50,50,50       | A Circle    | This is a description of my circle
- rect   | 72,144,215,216 | A rectangle | This is a description of my rectangle.

\@image: map="one" src="chapters/images/imagemap.png"

@text
Will generate the following imagemap:

@imagemap: id="one"
- shape  | coords         | Label       | Description
- circle | 50,50,50       | A Circle    | This is a description of my circle
- rect   | 72,144,215,216 | A rectangle | This is a description of my rectangle.

@image: map="one" src="chapters/images/imagemap.png"
