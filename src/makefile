include version.inc
include os.inc

# Display a list of available targets
help:
	@${echo} "Available Targets:"
	@${echo} "=================="
	@${echo} " cairo_plugin = build the cairo plugin"
	@${echo} " package      = build shorte and generate the tarball"
	@${echo} " install      = install shorte over the network"
	@${echo} " exe          = build a standalone executable"
	@${echo} " docs         = generate the documentation for the site"
	
	@${echo} " tests        = run the test suite to generate the list of sample documents"
	@${echo} "   test_headings   = test the use of heading tags"
	@${echo} "   test_textblocks = test the @textblock tag"
	@${echo} "   test_tables     = test the @table tag"
	@${echo} "   test_code       = test the parsing of C code"
	@${echo} "   test_code_quick = test the parsing of C code but only generate HTML for faster results"
	@${echo} "   test_functions  = test the @prototype source code tag"
	@${echo} "   test_enums      = test the @enum source code tag"
	@${echo} "   test_bullets    = test the @ul and @ol list tags"
	@${echo} "   test_wkiwords   = test the use of wikiwords"

env:
	@${echo} " SHELL: ${SHELL}"

all:
	make package

# Build the cairo plugin used for generating
# images.
cairo_plugin:
	cd ${cairo_path} && make

# This target is used to package up shorte into a tarball
# for distribution
package: cairo_plugin
	rm -rf ../build-output
	${mkdir} -p ../build-output
	${mkdir} -p ../build-output/3rdparty
	cp -r *.py ../build-output
	cp -r *.cfg ../build-output
	cp -r syntax ../build-output
	cp -r templates ../build-output
	cp -r src ../build-output
	cp -r libs ../build-output/libs
#	cp -r 3rdparty/batik ../build-output/3rdparty/batik
	cp release_notes.tpl ../build-output/.
	rm -rf ../build-output/libs/lib32
	rm -rf ../build-output/libs/lib64
	cd ../build-output && cat shorte.py | sed "s/<<VERSION>>/${version}/" > shorte2.py
	cd ../build-output && mv shorte2.py shorte.py && chmod 755 shorte.py
	cd ../build-output && rm -rf *.pyc
	cd ../build-output && chmod -R o+x *
	cd ../build-output && chmod -R o+r *
	cd ../build-output && chmod -R g+x *
	cd ../build-output && chmod -R g+r *
	cd ../build-output && chmod 755 .
	cd ../build-output && find . -type d -exec chmod "o+x" {} \;
	cd ../build-output && ${archive}

win32:
	rm -rf ../build-output
	mkdir -p ../build-output
#	mkdir -p ../build-output/3rdparty
	cp -r *.py ../build-output
	cp -r *.cfg ../build-output
	cp -r syntax ../build-output
	cp -r templates ../build-output
	cp -r libs ../build-output/libs
#	cp -r 3rdparty/batik ../build-output/3rdparty/batik
	cp release_notes.tpl ../build-output/.
	rm -rf ../build-output/libs/lib32
	rm -rf ../build-output/libs/lib64
	cd ../build-output && cat shorte.py | sed "s/<<VERSION>>/${version}/" > shorte2.py
	cd ../build-output && mv shorte2.py shorte.py && chmod 755 shorte.py
	cd ../build-output && zip -r shorte-${version}.zip *

vim:
	cp syntax/vim/syntax/tpl.vim /cygdrive/c/Program\ Files/Vim/vim73/syntax/.

install:
	cd ../build-output && cp -r shorte-${version}.tar.gz /cygdrive/m/shorte/.
	ssh belliott@jenkins 'cd /home/belliott/modules/buildenv && cat makefile | sed -e "s/pkg_shorte:=shorte-1.0.[0-9]*/pkg_shorte:=shorte-${version}/" > makefile2;\
	cd /home/belliott/modules/buildenv && make -f makefile2 download_shorte && make -f makefile2 build_shorte;\
	cd /home/belliott/modules/buildenv/modulefiles/shorte && cat 1.0.10 | sed -e "s/1.0.10/${version}/" > ${version};\
	cd /home/belliott/modules/buildenv/modulefiles/shorte && cat .version | sed -e "s/1.0.[0-9]*/${version}/" > .version.new;\
	cd /home/belliott/modules/buildenv/modulefiles/shorte && mv .version .version.bak && mv .version.new .version;\
	cd /home/belliott/modules/buildenv && make -f makefile2 install_module_files;\
	cd /home/belliott/modules/buildenv && make -f makefile2 install_module_files'

tag:
	git tag SHORTE_VERSION_${version_str}
	

tests:
	rm -rf build-output
	make test_hello
	make test_headings
	make test_textblocks
	make test_tables
	make test_code
	make test_functions
	make test_enums
	make test_bullets
	make test_wikwords

test_hello:
	python shorte.py -f examples/hello.tpl -p "html+pdf" -o build-output/hello

test_headings:
	python shorte.py -f examples/headings.tpl -p "html+pdf" -o build-output/headings

test_textblocks:
	python shorte.py -f examples/textblocks.tpl -o build-output/textblock -p "html+pdf"

test_tables:
	python shorte.py -f examples/tables.tpl -p "html+pdf" -o build-output/tables

test_code:
	python shorte.py -f examples/test.c -x cpp -o build-output/c_code -p "html+pdf"
	python shorte.py -f examples/test.h -x cpp -o build-output/c_code_header -p "html+pdf"
	python shorte.py -f examples/test.c -x cpp -o build-output/c_code -p "shorte"

test_code_quick:
	python shorte.py -f examples/test.c -x cpp -o build-output/c_code -p "html"
	python shorte.py -f examples/test.h -x cpp -o build-output/c_code_header -p "html"
	python shorte.py -f examples/test.c -x cpp -o build-output/c_code -p "shorte"

test_functions:
	python shorte.py -f examples/functions.tpl -o build-output/functions -p "html+pdf"

test_enums:
	python shorte.py -f examples/enums.tpl -p "html+pdf" -o build-output/enums

test_bullets:
	python shorte.py -f examples/bullets.tpl -p "html_inline+pdf" -o build-output/bullets

test_t100:
	python shorte.py -f examples/cs_t100_api.h -x cpp -p "html_inline" -o build-output/t100

test_wikiwords:
	python shorte.py -f examples/wikiwords.tpl -p "html+pdf" -o build-output/wikiwords

test_junk:
#	python shorte.py -f "examples/test.c examples/test.h" -x cpp -p shorte -o build-output/code
#	python shorte.py -f "build-output/code/test.h.tpl build-output/code/test.tpl" -p html -o build-output/code_to_html
	python shorte.py -f examples/test.c -x cpp -o build-output/c_code -p "html+pdf"
	python shorte.py -f examples/test.c -x cpp -o build-output/c_code -p "html"
	python shorte.py -f examples/test.h -x cpp -o build-output/c_code_header -p "html"
	python shorte.py -f examples/code.tpl -p html_inline -o build-output/html
	python shorte.py -f examples/functions.tpl -p "html+pdf" -o build-output/functions
	python shorte.py -f examples/functions.tpl -p "html_inline+pdf" -o build-output/functions
	python shorte.py -f examples/hello.tpl -o build-output/hello -p "html+pdf"

exe:
	rm -rf dist
	c:/usr/tools/python/python setup.py py2exe
	cp C:/usr/cvs/hsio/3rdparty/msvc/MSVCR100.dll dist
	cd dist && zip -r shorte.${version}.zip *

tarball:
	

docs:
	cd ../docs && make pdf

# This target is used to package up shorte into a tarball
# for distribution
release:
	rm -rf ../build-output
	${mkdir} -p ../build-output
	cp -r *.py ../build-output
	rm -rf ../build-output/setup.py
	rm -rf ../build-output/mediawiki_parser.py
	cp -r *.cfg ../build-output
	cp -r makefile.customer ../build-output/makefile
	cp -r os.inc ../build-output
	cp -r version.inc ../build-output
	cp -r syntax ../build-output
	cp -r src ../build-output/.
	-rm -rf ../build-output/src/templates/*.pyc
	-rm -rf ../build-output/src/graphing/*.pyc
	cp -r libs ../build-output/.
	-rm -rf ../build-output/libs/cygwin
	-rm -rf ../build-output/libs/osx
	-rm -rf ../build-output/libs/*.pyc
	-rm -rf ../build-output/libs/win32
	-rm -rf ../build-output/libs/*.dll
	-rm -rf ../build-output/libs/*.pdb
	-rm -rf ../build-output/libs/*.lib
	-rm -rf ../build-output/libs/*.cxx
	-rm -rf ../build-output/libs/build.old
	-rm -rf ../build-output/libs/3rdparty
	-rm -rf ../build-output/libs/*.pyd
	-rm -rf ../build-output/libs/*.exp
	cp -r templates ../build-output/.
	-rm -rf ../build-output/templates/html/exar
	-rm -rf ../build-output/templates/html_inline/exar
	-rm -rf ../build-output/templates/c/exar*
	-rm -rf ../build-output/templates/css
	-rm -rf ../build-output/templates/logos
	-rm -rf ../build-output/templates/photoshop
	-rm -rf ../build-output/templates/powerpoint
	-rm -rf ../build-output/templates/swig
	-rm -rf ../build-output/templates/vera
	-rm -rf ../build-output/templates/word
	-rm -rf ../build-output/templates/odt/cortina
	-rm -rf ../build-output/templates/odt/cortina_public
	-rm -rf ../build-output/templates/odt/images
	-rm -rf ../build-output/templates/odt/convert_to_pdf_stripped.odt
	-rm -rf ../build-output/templates/odt/cortina.backup.odt
	-rm -rf ../build-output/templates/odt/cortina_public.backup.odt
	-rm -rf ../build-output/templates/odt/page_header_logo.png
	cp -r examples ../build-output/.
	-rm ../build-output/examples/.*.swp
	-rm ../build-output/examples/*.swf
	-rm -rf ../build-output/examples/blah.tpl
	-rm -rf ../build-output/examples/code.tpl
	-rm -rf ../build-output/examples/simple.tpl
	-rm -rf ../build-output/examples/hello.tpl
	-rm -rf ../build-output/examples/cs_t100*
	-rm -rf ../build-output/examples/ideas.tpl
	-rm -rf ../build-output/examples/imagemap.tpl
	-rm -rf ../build-output/examples/mdio.tpl
	-rm -rf ../build-output/examples/nested_tables.tpl
	-rm -rf ../build-output/examples/php.tpl
	-rm -rf ../build-output/examples/*.png
	-rm -rf ../build-output/examples/*.svg
	-rm -rf ../build-output/examples/test.tpl
	-rm -rf ../build-output/examples/tmp.tpl
	cd ../build-output && tar -czf shorte.${version}.tar.gz *

#	cp -r src ../build-output
#	cp -r libs ../build-output/libs
##	cp -r 3rdparty/batik ../build-output/3rdparty/batik
#	cp release_notes.tpl ../build-output/.
#	rm -rf ../build-output/libs/lib32
#	rm -rf ../build-output/libs/lib64
#	cd ../build-output && cat shorte.py | sed "s/<<VERSION>>/${version}/" > shorte2.py
#	cd ../build-output && mv shorte2.py shorte.py && chmod 755 shorte.py
#	cd ../build-output && rm -rf *.pyc
#	cd ../build-output && chmod -R o+x *
#	cd ../build-output && chmod -R o+r *
#	cd ../build-output && chmod -R g+x *
#	cd ../build-output && chmod -R g+r *
#	cd ../build-output && chmod 755 .
#	cd ../build-output && find . -type d -exec chmod "o+x" {} \;
#	cd ../build-output && ${archive}
