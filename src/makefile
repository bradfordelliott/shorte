include version.inc

help:
	@echo "Available Targets"
	@echo "================="
	@echo " package = build shorte and generate the tarball"
	@echo " install = install shorte over the network"

all:
	make package

cairo_plugin:
	cd ../shorte_libs/unix && make

package: cairo_plugin
	rm -rf ../build-output
	mkdir -p ../build-output
	mkdir -p ../build-output/3rdparty
	cp -r *.py ../build-output
	cp -r *.cfg ../build-output
	cp -r syntax ../build-output
	cp -r templates ../build-output
	cp -r src ../build-output
	cp -r libs ../build-output/libs
	cp -r 3rdparty/batik ../build-output/3rdparty/batik
	cp release_notes.tpl ../build-output/.
	rm -rf ../build-output/libs/lib32
	rm -rf ../build-output/libs/lib64
	cd ../build-output && cat shorte.py | sed "s/<<VERSION>>/${version}/" > shorte2.py
	cd ../build-output && mv shorte2.py shorte.py && chmod 755 shorte.py
	cd ../build-output && tar -czf shorte-${version}.tar.gz *

win32:
	rm -rf ../build-output
	mkdir -p ../build-output
	mkdir -p ../build-output/3rdparty
	cp -r *.py ../build-output
	cp -r *.cfg ../build-output
	cp -r syntax ../build-output
	cp -r templates ../build-output
	cp -r libs ../build-output/libs
	cp -r 3rdparty/batik ../build-output/3rdparty/batik
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
	ssh belliott@rhfarm32 'cd /home/belliott/modules/buildenv && cat makefile | sed -e "s/pkg_shorte:=shorte-1.0.[0-9]*/pkg_shorte:=shorte-${version}/" > makefile2'
	ssh belliott@rhfarm32 'cd /home/belliott/modules/buildenv && make -f makefile2 download_shorte && make -f makefile2 build_shorte'
	ssh belliott@rhfarm32 'cd /home/belliott/modules/buildenv/modulefiles/shorte && cat 1.0.10 | sed -e "s/1.0.10/${version}/" > ${version}'
	ssh belliott@rhfarm32 'cd /home/belliott/modules/buildenv/modulefiles/shorte && cat .version | sed -e "s/1.0.[0-9]*/${version}/" > .version.new'
	ssh belliott@rhfarm32 'cd /home/belliott/modules/buildenv/modulefiles/shorte && mv .version .version.bak && mv .version.new .version'
	ssh belliott@rhfarm32 'cd /home/belliott/modules/buildenv && make -f makefile2 install_module_files'
	ssh belliott@belliott-linux 'cd /home/belliott/modules/buildenv && make -f makefile2 install_module_files'

tag:
	git tag SHORTE_VERSION_${version_str}
	

tests:
    # Parse some C code
	shorte.py -f examples/test.c -x cpp -o build-output/c_code
	shorte.py -f examples/test.h -x cpp -o build-output/c_code_header
	shorte.py -f examples/code.tpl -p html_inline -o build-output/html
