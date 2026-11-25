#!/usr/bin/env bash
# Check each planted defect separately against System A's sources. Usage: probes/types/run.sh SCRATCHDIR
set -u
here="$(cd "$(dirname "$0")" && pwd)"; root="$here/../.."; s="$1"
mkdir -p "$s/src"; cp "$root/flix.toml" "$s/"; ln -sfn "$root/lib" "$s/lib"
for f in "$root"/src/*.flix; do ln -sf "$f" "$s/src/"; done
for t in "$here"/T*.flix "$here"/E*.flix; do
  n=$(basename "$t" .flix); cp "$t" "$s/src/TypeProbe.flix"
  out=$(cd "$s" && flix check 2>&1 | sed $'s/\x1b\\[[0-9;]*m//g')
  hdr=$(printf '%s\n' "$out" | grep -E '^-- .* Error' | head -3 | sed 's/ -*  *src.*//' | paste -sd ';' -)
  msg=$(printf '%s\n' "$out" | grep -E '^>> ' | head -1) 
  echo "$n | ${hdr:-NOT CAUGHT} | $msg | $(head -1 "$t" | sed 's|^// ||')"
done
rm -f "$s/src/TypeProbe.flix"
