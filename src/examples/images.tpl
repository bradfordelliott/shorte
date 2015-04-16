@doctitle Shorte Examples
@docsubtitle Images

#@docbanner "examples/gallery/banner.png"

@body
@h1 Images

@h2 200px
@image: src="examples/test.png" width="200px"

@h2 300px
@image: src="examples/test.png" width="300px"

@h2 700px
@image: src="examples/record_0.png" width="700px"

@h2 80%
@image: src="examples/record_0.png" width="80%"

@h2 1400px
@image: src="examples/record_0.png" width="1400px"

@h2 No Sizing
@image: src="examples/record_0.png"

@h2 Gallery
This is some random text with a gallery

@gallery:
-- images:
-h Image                     | Size  | Caption
- examples/gallery/one.jpg   | 70    | This is an example caption that is really long. Not sure if it will wrap or not. Hopefully
                                         it won't wrap and I won't have any real issues with it because I don't want to have any issues.
- examples/gallery/two.jpg   | 70    | This is my caption
- examples/gallery/three.jpg | 70    | This is my caption

@text
This is some other random information

@gallery
-- images:
-h Image                     | Size  | Caption
- examples/gallery/four.jpg  | 300   | This is my caption
