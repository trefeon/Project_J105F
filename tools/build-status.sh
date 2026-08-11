#!/bin/bash
# Build status + ETA sampler for the zImage build on vps-01
cd ~/j105f/android_kernel_samsung_j1mini3g || exit 1
LOG=~/j105f/build-zimage.log

echo "== last log line =="
tail -1 "$LOG"
echo "== zImage =="
ls -la arch/arm/boot/zImage 2>/dev/null || echo "not yet"
echo "== resources =="
free -m | head -2
swapon --show | tail -1
echo "== progress =="
C1=$(grep -c '^  CC\|^  LD\|^  AR' "$LOG")
OBJ1=$(find . -name '*.o' 2>/dev/null | wc -l)
TOTALC=$(find arch/arm drivers fs net kernel mm security sound ipc init block crypto -name '*.c' 2>/dev/null | wc -l)
echo "compiled_lines=$C1 objects=$OBJ1 total_c_files~=$TOTALC"
sleep 45
C2=$(grep -c '^  CC\|^  LD\|^  AR' "$LOG")
OBJ2=$(find . -name '*.o' 2>/dev/null | wc -l)
RATE=$((C2-C1))
echo "rate=$RATE files/45s"
if [ "$RATE" -gt 0 ]; then
  REMAIN=$(( (TOTALC - OBJ2) / (RATE * 4 / 3) ))
  echo "estimated remaining ~$(( REMAIN / 60 )) min (objects proxy, rough)"
fi
echo "== last log line again =="
tail -1 "$LOG"
