#!/usr/bin/env bash
# Set up a Lean project (Mathlib pin) for grading: fetch dependencies and the
# prebuilt Mathlib cache, then build PhysProofBench. Needs internet (run on a
# login node; grading itself works offline).
#
#   scripts/setup-pin.sh lean        # main pin (Lean/Mathlib v4.34)
#   scripts/setup-pin.sh lean-v4.9   # Lean 4.9-era pin (specialist provers)
#
# Workarounds needed for old pins, applied automatically:
# - Some dependency revisions pinned by 2024 Mathlib are no longer on any
#   branch, so `git clone` doesn't contain them and Lake's checkout fails
#   ("git exited with code 128"). They are still fetchable by hash; this
#   script fetches each one and retries.
# - macOS only: executables linked by the 2024 toolchain (Mathlib's `cache`
#   tool) are rejected by newer dyld ("__DATA_CONST segment missing
#   SG_READ_ONLY flag"). The script sets that flag and re-signs the binary.
#   Linux is unaffected.
set -euo pipefail
PIN="${1:?usage: $0 <lean-project-dir>}"
cd "$(dirname "$0")/../$PIN"

for attempt in $(seq 1 15); do
  # `lake env` materializes dependencies from the committed lake-manifest.json
  # (it does not upgrade them, unlike `lake update`).
  out=$(lake env true 2>&1) || true
  if ! echo "$out" | grep -q "exited with code 128"; then
    break
  fi
  # The package Lake was cloning or checking out when git failed, and the
  # revision the manifest pins it to.
  name=$(echo "$out" | grep -oE "info: [A-Za-z0-9_-]+: (cloning|updating repository)" | tail -1 \
         | sed -E 's/info: ([A-Za-z0-9_-]+):.*/\1/')
  rev=$(python3 -c "import json,sys; m=json.load(open('lake-manifest.json')); print(next(p['rev'] for p in m['packages'] if p['name']==sys.argv[1]))" "$name")
  dir=".lake/packages/$name"
  if [ -z "$name" ] || [ -z "$rev" ] || [ ! -d "$dir" ]; then echo "$out"; exit 1; fi
  echo "fetching orphaned revision $rev of $name"
  git -C "$dir" fetch -q origin "$rev"
  git -C "$dir" checkout -q "$rev"
done

CACHE=.lake/packages/mathlib/.lake/build/bin/cache
if ! lake exe cache get; then
  # Typically the macOS dyld rejection described above: patch, run directly.
  if [ "$(uname)" = Darwin ] && [ -x "$CACHE" ]; then
    python3 - "$CACHE" <<'PY'
import struct, sys
p = sys.argv[1]; d = bytearray(open(p, "rb").read())
ncmds = struct.unpack_from("<I", d, 16)[0]
off = 32
for _ in range(ncmds):
    cmd, size = struct.unpack_from("<II", d, off)
    if cmd == 0x19 and d[off + 8:off + 24].rstrip(b"\0") == b"__DATA_CONST":
        fo = off + 68  # segment_command_64.flags (after cmd, cmdsize, segname[16], 4x u64, 3x u32)
        struct.pack_into("<I", d, fo, struct.unpack_from("<I", d, fo)[0] | 0x10)
    off += size
open(p, "wb").write(d)
PY
    codesign -s - -f "$CACHE"
    lake env "$CACHE" get
  else
    exit 1
  fi
fi
lake build Mathlib PhysProofBench
echo "pin $PIN ready"
