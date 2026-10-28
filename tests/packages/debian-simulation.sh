#!/bin/sh
# Run inside a disposable, provisioned Debian 13 container; never installs KDE.
set -eu
output=${1:?output directory required}
mkdir -p "$output"
dpkg-query -W > "$output/packages-before.txt"
/usr/bin/python3 -I /source/packaging/debian/udm_packages.py plan > "$output/debian-plan.json"
/usr/bin/python3 -I /source/packaging/debian/udm_packages.py plan > "$output/debian-plan-repeat.json"
/usr/bin/python3 -I /source/packaging/debian/udm_packages.py verify > "$output/debian-before.json"
dpkg-query -W > "$output/packages-after.txt"
cmp "$output/packages-before.txt" "$output/packages-after.txt"
/usr/bin/python3 - "$output" <<'PY'
import hashlib
import json
from pathlib import Path
import sys
root = Path(sys.argv[1])
review = json.loads((root / 'debian-plan.json').read_text())
assert review == json.loads((root / 'debian-plan-repeat.json').read_text())
plan = review['plan']
assert plan['install'] and not plan['remove'] and not plan['upgrade']
assert all(p['version'] and p['origins'] for p in plan['install'])
assert not {p['name'] for p in plan['install']} & {'sddm', 'gdm3', 'lightdm', 'xdm'}
verification = json.loads((root / 'debian-before.json').read_text())
assert verification['ready'] is False
assert verification['session_started'] is False
assert verification['live_switch_capable'] is False
print(json.dumps(dict(install_count=len(plan['install']), digest=review['digest'],
                     inventory_sha256=hashlib.sha256((root / 'packages-before.txt').read_bytes()).hexdigest()), indent=2))
PY
