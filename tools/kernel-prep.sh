#!/bin/bash
# Phase 1.1 — prepare + launch kernel build on vps-01 (runs in background via nohup)
set -e
cd ~/j105f/android_kernel_samsung_j1mini3g

echo "== applying pmOS patches =="
for p in *.patch; do
  if patch -p1 --dry-run -s < "$p" > /dev/null 2>&1; then
    patch -p1 -s < "$p" > /dev/null 2>&1 && echo "OK   $p"
  else
    echo "FAIL $p"
  fi
done

echo "== config =="
cp config-samsung-j1mini3g.armv7 .config
make ARCH=arm CC=arm-linux-gnueabihf-gcc olddefconfig > /tmp/olddef.log 2>&1 || echo "olddefconfig rc=$?"
tail -2 /tmp/olddef.log

echo "== starting build =="
nohup make ARCH=arm CC=arm-linux-gnueabihf-gcc -j2 KBUILD_BUILD_VERSION='1-postmarketOS' zImage \
  > ~/j105f/build-zimage.log 2>&1 &
echo "BUILD_PID=$!"
