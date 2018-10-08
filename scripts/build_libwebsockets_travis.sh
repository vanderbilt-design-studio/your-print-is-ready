#!/bin/bash
if [ -z ${TRAVIS_BUILD_DIR+x} ]; then export TRAVIS_BUILD_DIR=$HOME/your-print-is-ready; else echo "This is Travis"; fi
export OPENSSL_ROOT_DIR=$TRAVIS_BUILD_DIR/libs/openssl
export OPENSSL_INCLUDE_DIR=$OPENSSL_ROOT_DIR/include
export OPENSSL_CRYPTO_LIBRARY=$OPENSSL_ROOT_DIR/libcrypto.so
export OPENSSL_SSL_LIBRARY=$OPENSSL_ROOT_DIR/libssl.so
export MACHINE=armv7
export ARCH=arm
export BIN_DIR=$TRAVIS_BUILD_DIR/tools/arm-bcm2708/arm-rpi-4.9.3-linux-gnueabihf/bin/
export CC=$BIN_DIR/arm-linux-gnueabihf-gcc
export AR="$BIN_DIR/arm-linux-gnueabihf-ar"
export RANLIB="$BIN_DIR/arm-linux-gnueabihf-ranlib"

cd $TRAVIS_BUILD_DIR/libs/libwebsockets
make clean
cmake -DOPENSSL_ROOT_DIR="$OPENSSL_ROOT_DIR" -DOPENSSL_INCLUDE_DIR="$OPENSSL_INCLUDE_DIR" -DOPENSSL_CRYPTO_LIBRARY="$OPENSSL_CRYPTO_LIBRARY" -DOPENSSL_SSL_LIBRARY="$OPENSSL_SSL_LIBRARY" -DCMAKE_TOOLCHAIN_FILE=../../cmake/toolchain/toolchain-rpi-travis-c.cmake . && make -j$(nproc)
cd -