
llvm_version:=3.6.1
llvm_compilerrt_version:=3.6.1
llvm_compilerrt_ext:=.src
tar_xtension:=xz
tar_flag:=J
clang_name:=cfe

#llvm_version:=3.4.2
#llvm_compilerrt_version:=3.4
#llvm_compilerrt_ext:=
#tar_xtension:=gz
#tar_flag:=z
#clang_name:=cfe

#llvm_version:=3.2
#llvm_compilerrt_version:=3.2
#llvm_compilerrt_ext:=.src
#tar_xtension:=gz
#tar_flag:=z
#clang_name:=clang

download:
	wget http://llvm.org/releases/${llvm_version}/llvm-${llvm_version}.src.tar.${tar_xtension}
	wget http://llvm.org/releases/${llvm_version}/${clang_name}-${llvm_version}.src.tar.${tar_xtension}
	wget http://llvm.org/releases/${llvm_compilerrt_version}/compiler-rt-${llvm_compilerrt_version}.src.tar.${tar_xtension}

extract:
	rm -rf llvm.${llvm_version}/tools/clang
	rm -rf llvm.${llvm_version}/projects/compiler-rt
	rm -rf llvm-${llvm_version}.src
	rm -rf cfe-${llvm_version}.src
	rm -rf compiler-rt-${llvm_version}${llvm_compilerrt_ext}
	tar -x${tar_flag}f llvm-${llvm_version}.src.tar.${tar_xtension}
	mv llvm-${llvm_version}.src llvm.${llvm_version}
	tar -x${tar_flag}f ${clang_name}-${llvm_version}.src.tar.${tar_xtension}
	mv ${clang_name}-${llvm_version}.src llvm.${llvm_version}/tools/clang
	tar -x${tar_flag}f compiler-rt-${llvm_compilerrt_version}.src.tar.${tar_xtension}
	mv compiler-rt-${llvm_compilerrt_version}${llvm_compilerrt_ext} llvm.${llvm_version}/projects/compiler-rt

build:
	mkdir build.${llvm_version}
	cd build.${llvm_version} && cmake -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_THREADS=OFF ../llvm.${llvm_version}
	cd build.${llvm_version} && make -j8 libclang

test:
	rm -rf ../cygwin/test/${llvm_version}
	mkdir ../cygwin/test/${llvm_version}
	cp build.${llvm_version}/bin/cygclang.dll ../cygwin/test/${llvm_version}/.
	cp -r llvm.${llvm_version}/tools/clang/bindings/python/clang ../cygwin/test/${llvm_version}/.

