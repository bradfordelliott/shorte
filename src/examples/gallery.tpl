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
