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
	@${echo} " release_notes = generate the release notes for shorte"
	@${echo} ""
	
	@${echo} " tests        = run the test suite to generate the list of sample documents"
	@${echo} "   test_hello           = A hello world example for shorte"
	@${echo} "   test_headings        = test the use of heading tags"
	@${echo} "   test_textblocks      = test the @textblock tag"
	@${echo} "   test_tables          = test the @table tag"
	@${echo} "   test_code            = test the parsing of C code"
	@${echo} "   test_code_quick      = test the parsing of C code but"
	@${echo} "                          only generate HTML for faster results"
	@${echo} "   test_functions       = test the @prototype source code tag"
	@${echo} "   test_enums           = test the @enum source code tag"
	@${echo} "   test_bullets         = test the @ul and @ol list tags"
	@${echo} "   test_wkiwords        = test the use of wikiwords"
	@${echo} "   test_images          = test the use of images"
	@${echo} "   test_mergefile       = test the generation of mergefiles used for diffing"
	@${echo} "   test_sql             = test the generation of SQL databases to store source code annotations"
	@${echo} "   test_defines         = test the formatting of defines"
	@${echo} "   test_extract_private = test for extracting private methods"
	@${echo} "   test_revealjs        = test for reveal.js presentations"
	@${echo} "   test_comments        = test for single and multi-line comment handling"
	@${echo} "   test_sequences       = test for sequence diagrams"
	@${echo} "   test_templates       = test all the templates"

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

release_notes:
	python shorte.py -f release_notes.tpl -p html_inline -t ${THEME} -v ${version} -o build-output/release_notes

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
	make test_api_reference
	make test_defines
	make test_functions
	make test_enums
	make test_bullets
	make test_wikiwords
	make test_conditionals
	make test_images
	make test_mergefile
	make test_sql
	make test_server
	make test_extract_private
	make test_revealjs
	make test_mx
	make test_templates

THEME:=shorte

test_mx:
	python shorte.py -f SRSA.tpl -p "html+pdf" -t "html=cortina_web;pdf=cortina" -w "examples/mx" -o build-output/mx

test_hello:
#	python shorte.py -f examples/hello.tpl -t "${THEME}" -p "html+pdf" -o build-output/hello
#	python shorte.py -f examples/hello.tpl -p "html+pdf" -t "html=cortina_web;pdf=cortina_transport" -o build-output/hello
	python shorte.py -f examples/hello.tpl -p "html+pdf" -t "html=cortina_web;pdf=cortina" -o build-output/hello_hsio

test_headings:
	python shorte.py -f examples/headings.tpl -t "${THEME}" -p "html+pdf" -o build-output/headings

test_textblocks:
	python shorte.py -f examples/textblocks.tpl -t "${THEME}" -o build-output/textblock -p "html+pdf"
	python shorte.py -f examples/textblocks.tpl -t "${THEME}" -o build-output/textblock_inline -p "html_inline+pdf"

test_tables:
	python shorte.py -f examples/tables.tpl -t "${THEME}" -p "html+pdf" -o build-output/tables

test_api_reference:
	python shorte.py -f examples/api_reference.tpl -t "${THEME}" -o build-output/api_reference -p "html+pdf" -s "shorte.auto_summarize=0"
	python shorte.py -f examples/api_reference.tpl -t "${THEME}" -o build-output/api_reference -p "shorte"

test_code:
	python shorte.py -f examples/code.tpl -t "${THEME}" -o build-output/code.tpl -p "html+pdf"
	python shorte.py -f examples/test.c -t "${THEME}" -x cpp -o build-output/c_code -p "html+pdf"
	python shorte.py -f examples/test.h -t "${THEME}" -x cpp -o build-output/c_code_header -p shorte
	python shorte.py -f examples/test.h -t "${THEME}" -x cpp -o build-output/c_code_header -p "html+pdf"
	python shorte.py -f examples/test.c -t "${THEME}" -x cpp -o build-output/c_code -p "shorte"
    # DEBUG BRAD: This target is currently failing. Not sure how easy it will be to fix.
	python shorte.py -f "examples/headings.tpl build-output/c_code/test.tpl" -t "${THEME}" -o build-output/c_code_error -p "html+pdf"

# This is an intermediate way of preprocessing files until I can add proper
# support to shorte.
test_preprocessor:
	cat examples/cs_t100_api.h | sed 's/#\(define\|include\)/@@\1/g' | gcc -E -C - | src/parsers/gcc_expand.py > cs_t100_api_preprocessed.h
	cat examples/test.c | sed 's/#\(define\|include\)/@@\1/g' | gcc -E -C - | src/parsers/gcc_expand.py > examples/test_preprocessed.c
	python shorte.py -f examples/cs_t100_api_preprocessed.h -t "${THEME}" -x cpp -o build-output/c_code_t100_preprocessed -p "html+pdf"
	python shorte.py -f examples/test_preprocessed.c -t "${THEME}" -x cpp -o build-output/c_code_preprocessed -p "html+pdf"

test_defines:
	python shorte.py -f examples/defines.h -t "${THEME}" -x cpp -o build-output/defines -p "html+pdf"


test_code_quick:
	python shorte.py -f examples/test.c -t "${THEME}" -x cpp -o build-output/c_code -p "html"
	python shorte.py -f examples/test.h -t "${THEME}" -x cpp -o build-output/c_code_header -p "html"
	python shorte.py -f examples/test.c -t "${THEME}" -x cpp -o build-output/c_code -p "shorte"
	python shorte.py -f examples/test.c -t "${THEME}" -x cpp -o build-output/c_code -p "txt"

test_functions:
	python shorte.py -f examples/functions.tpl -t "${THEME}" -o build-output/functions -p "html+pdf"

test_enums:
	python shorte.py -f examples/enums.tpl -t "${THEME}" -p "html+pdf" -o build-output/enums

test_bullets:
	python shorte.py -f examples/bullets.tpl -t "html=cortina_web;pdf=cortina" -p "html+pdf" -o build-output/bullets --zip=bullets.zip
	python shorte.py -f examples/bullets.tpl -t "html=shorte;pdf=shorte" -p "html+pdf" -o build-output/bullets_shorte
	python shorte.py -f examples/bullets.tpl -t "html=cortina_web;pdf=cortina_public" -p "html_inline+pdf" -o build-output/bullets_public --zip=bullets.zip
	python shorte.py -f examples/bullets.tpl -t "html=cortina_web;pdf=cortina" -p "html_inline+pdf" -o build-output/bullets_inline --zip=bullets_inline.zip

test_t100:
	python -m cProfile -s time shorte.py -f examples/cs_t100_api.h -t "cortina_web" -x cpp -p "html_inline" -o build-output/t100

test_wikiwords:
	python shorte.py -f examples/wikiwords.tpl -t "${THEME}" -p "html+pdf" -o build-output/wikiwords

test_conditionals:
	python shorte.py -f examples/conditionals.tpl -t "${THEME}" -p "html+pdf" -o build-output/conditionals

test_images:
	python shorte.py -f examples/images.tpl -t "${THEME}" -p "html+pdf" -o build-output/images
	python shorte.py -f examples/test.png -i "encode_images" 

# This example is used to test the generation of mergefiles. A mergefile is a target that
# assembles a list of shorte files into a single document. This is useful for diffing things
# in one assembly rather than trying to diff the output.
test_mergefile:
	python shorte.py -f "examples/images.tpl examples/headings.tpl" -t "${THEME}" -p mergefile -o build-output/mergefile
	python shorte.py -f "build-output/mergefile/book.tpl" -t "${THEME}" -p "html+pdf" -o build-output/mergefile

test_sql:
	python shorte.py -f "examples/test.c examples/test.h" -t "${THEME}" -x cpp -o build-output/sql -p "sql"

# This method is called to launch a test server and then generate several example documents.
test_server:
	mkdir -p build-output/server_example
	python shorte.py --server --port=8400 &
	sleep 1
	python server_test.py --package="html_inline" --theme="cortina_web" --ip=127.0.0.1 --port=8400 > build-output/server_example/server_example.html
	python server_test.py --package="html_inline+pdf" --theme="html=cortina_web;pdf=cortina_public" --zip --ip=127.0.0.1 --port=8400 > build-output/server_example/server_example2.zip
	python server_test.py --shutdown --ip=127.0.0.1 --port=8400

test_extract_private:
	python shorte.py -s "cpp_parser.extract_private=1" -f examples/test.h -x cpp -p "html+pdf" -o build-output/private_methods
	python shorte.py -s "cpp_parser.extract_private=0" -f examples/test.h -x cpp -o build-output/public_methods

test_revealjs:
	python shorte.py -f examples/presentation.tpl -p "reveal.js+pdf" --theme="reveal.js=shorte;pdf=shorte" -o build-output/presentation
	python shorte.py -f examples/presentation.tpl -p "reveal.js+txt" --theme="reveal.js=shorte" -o build-output/presentation2
	python shorte.py -f examples/headings.tpl -p "reveal.js" --theme=shorte -o build-output/presentation3
	python shorte.py -f examples/bullets.tpl -p "reveal.js" --theme=cortina -o build-output/presentation4

test_sequences:
	python shorte.py -f examples/sequences.tpl -p "reveal.js" --theme=shorte -o build-output/sequences
	python shorte.py -f examples/sequences.tpl -p "html+pdf" --theme=cortina -o build-output/sequences_pdf

test_templates:
	python shorte.py -f examples/template_test.tpl -p "txt" -o build-output/template_tests/text
	python shorte.py -f examples/template_test.tpl -p "word" -o build-output/template_tests/word
	python shorte.py -f examples/template_test.tpl -p "odt" -o build-output/template_tests/odt
	python shorte.py -f examples/template_test.tpl -p "mergefile" -o build-output/template_tests/mergefile
	python shorte.py -f examples/template_test.tpl -p "html" -o build-output/template_tests/html
	python shorte.py -f examples/template_test.tpl -p "reveal.js" -o build-output/template_tests/revealjs
	python shorte.py -f examples/template_test.tpl -p "twiki" -o build-output/template_tests/twiki
	python shorte.py -f examples/template_test.tpl -p "mediawiki" -o build-output/template_tests/mediawiki
	python shorte.py -f examples/template_test.tpl -p "c" -o build-output/template_tests/c
	python shorte.py -f examples/template_test.tpl -p "shorte" -o build-output/template_tests/shorte
	python shorte.py -f examples/template_test.tpl -p "sql" -o build-output/template_tests/sql


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

# This target builds shorte as an executable that can be distributed
# under Windows so that it is not necessary to re-distribute python
exe:
	rm -rf dist
	${PATH_PYTHON} setup.py py2exe
	cp libs/win32/msvc/msvcr100.dll dist
	cp shorte.cfg dist/.
	cp build-output/release_notes/index.html dist/release_notes.html
	cd dist && zip -r shorte.${version}.zip *

tarball:
	

docs:
	cd ../docs && make pdf

# This target is used to package up shorte into a tarball
# for distribution
release: release_notes
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
	cp build-output/release_notes/index.html ../build-output/release_notes.html
	find ../build-output -name "*.pyc" -delete
	find ../build-output -name "*.swp" -delete
	find ../build-output -name "bar.png" -delete
	find ../build-output -name "line.png" -delete
	cp -r libs ../build-output/.
#	-rm -rf ../build-output/libs/cygwin
#	-rm -rf ../build-output/libs/osx
#	-rm -rf ../build-output/libs/win32
	-rm -rf ../build-output/libs/win32/Release
	-rm -rf ../build-output/libs/win32/_cairo_access*
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
	-rm ../build-output/examples/*.swf
	-rm -rf ../build-output/examples/blah.tpl
	-rm -rf ../build-output/examples/code.tpl
	-rm -rf ../build-output/examples/simple.tpl
	-rm -rf ../build-output/examples/hello.tpl
	-rm -rf ../build-output/examples/cs_t100*
	-rm -rf ../build-output/examples/mx
	-rm -rf ../build-output/examples/ideas.tpl
	-rm -rf ../build-output/examples/imagemap.tpl
	-rm -rf ../build-output/examples/mdio.tpl
	-rm -rf ../build-output/examples/nested_tables.tpl
	-rm -rf ../build-output/examples/php.tpl
	-rm -rf ../build-output/examples/*.png
	-rm -rf ../build-output/examples/*.svg
	-rm -rf ../build-output/examples/test.tpl
	-rm -rf ../build-output/examples/tmp.tpl
	cd ../build-output && chmod -R o+x *
	cd ../build-output && chmod -R o+r *
	cd ../build-output && chmod -R g+x *
	cd ../build-output && chmod -R g+r *
	cd ../build-output && chmod 755 .
	cd ../build-output && find . -type d -exec chmod "o+x" {} \;
	cd ../build-output && ${archive}

release_win32:
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
	cp build-output/release_notes/index.html ../build-output/release_notes.html
	-rm -rf ../build-output/src/templates/*.pyc
	-rm -rf ../build-output/src/graphing/*.pyc
	-rm -rf ../build-output/src/parsers/*.pyc
	cp -r libs ../build-output/.
	-rm -rf ../build-output/libs/cygwin
	-rm -rf ../build-output/libs/osx
	-rm -rf ../build-output/libs/*.pyc
#	-rm -rf ../build-output/libs/win32
#	-rm -rf ../build-output/libs/*.dll
	-rm -rf ../build-output/libs/*.pdb
	-rm -rf ../build-output/libs/*.lib
	-rm -rf ../build-output/libs/*.cxx
	-rm -rf ../build-output/libs/build.old
	-rm -rf ../build-output/libs/3rdparty
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
	cd ../build-output && ${archive}


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
