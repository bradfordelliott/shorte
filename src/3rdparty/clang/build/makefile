
llvm_version:=3.6.1
download:
#	wget http://llvm.org/releases/${llvm_version}/llvm-${llvm_version}.src.tar.xz
#	wget http://llvm.org/releases/${llvm_version}/cfe-${llvm_version}.src.tar.xz
#	wget http://llvm.org/releases/3.6.1/compiler-rt-3.6.1.src.tar.xz
	rm -rf llvm/tools/clang
	rm -rf llvm/projects/compiler-rt
	rm -rf llvm-${llvm_version}.src
	rm -rf cfe-${llvm_version}.src
	rm -rf compiler-rt-${llvm_version}.src
	tar -xzf llvm-${llvm_version}.src.tar.xz
	mv llvm-${llvm_version}.src llvm
	tar -xzf cfe-${llvm_version}.src.tar.xz
	mv cfe-${llvm_version}.src llvm/tools/clang
	tar -xzf compiler-rt-${llvm_version}.src.tar.xz
	mv compiler-rt-${llvm_version}.src llvm/projects/compiler-rt

build:
	mkdir build
	cd build && cmake -G "Unix Makefiles" ../llvm

