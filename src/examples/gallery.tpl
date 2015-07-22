@doctitle Image Gallery
@docsubtitle My Images

@body
@h1 Image Gallery
@gallery: theme="jssor_slideshow" height="1024" width="768"
-- images:
-h Image                     | Size  | Caption
<?
result = ''
import os
for root, dirs, files in os.walk("./examples/gallery"):
    for file in files:
        if file.endswith(".jpg"):
            result += '- %s | 200 | %s\n' % (os.path.join(root, file), file)
?>

@gallery: theme="gallery" height="800" width="600"
-- images:
-h Image                     | Size  | Caption
<?
result = ''
import os
for root, dirs, files in os.walk("./examples/gallery"):
    for file in files:
        if file.endswith(".jpg"):
            result += '- %s | 200 | %s\n' % (os.path.join(root, file), file)
?>

@gallery: theme="gallery_modern" height="800" width="600"
-- images:
-h Image                     | Size  | Caption
<?
result = ''
import os
for root, dirs, files in os.walk("./examples/gallery"):
    for file in files:
        if file.endswith(".jpg"):
            result += '- %s | 200 | %s\n' % (os.path.join(root, file), "This is a caption here")
?>

@gallery: theme="gallery_magazine" height="800" width="600"
-- images:
-h Image                     | Size  | Caption
<?
result = ''
import os
for root, dirs, files in os.walk("./examples/gallery"):
    for file in files:
        if file.endswith(".jpg"):
            result += '- %s | 200 | %s\n' % (os.path.join(root, file), "This is a really long caption with some text here that tells a story about the image. It should wrap and still look reasonable. Hopefully that is the case.")
?>
