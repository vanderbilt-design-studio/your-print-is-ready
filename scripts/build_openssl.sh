#!/bin/bash
if [ -z ${TRAVIS_BUILD_DIR+x} ]; then export TRAVIS_BUILD_DIR=$HOME/your-print-is-ready; else echo "This is Travis"; fi
export OPENSSL_DIR=$TRAVIS_BUILD_DIR/libs/openssl
export MACHINE=armv7
export ARCH=arm
export BIN_DIR=$TRAVIS_BUILD_DIR/tools/arm-bcm2708/arm-rpi-4.9.3-linux-gnueabihf/bin/
export CC=$BIN_DIR/arm-linux-gnueabihf-gcc
export AR="$BIN_DIR/arm-linux-gnueabihf-ar"
export RANLIB="$BIN_DIR/arm-linux-gnueabihf-ranlib"

cd $OPENSSL_DIR
#./config --prefix=${OPENSSL_DIR} --openssldir=${OPENSSL_DIR} -fPIC -g no-shared && make -j$(nproc)
make clean
./config no-asm shared --prefix=$OPENSSL_DIR
make -j$(nproc)
cd -