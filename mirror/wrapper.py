#!/usr/bin/python3

import datetime
import subprocess
import sys

sys.path.append(".")  # noqa
sys.path.append("..")  # noqa

import filelock
import yaml

import mirror

MIRROR_DATA = mirror.MIRROR_DATA

lock = filelock.FileLock(
    MIRROR_DATA.parent / (MIRROR_DATA.name + ".lock"),
    timeout=10
)

if len(sys.argv[1:]) < 2:
    print(f"ERROR: bad usage, use '{sys.argv[0]} <mirror_name> <command>'")
    sys.exit(1)

mirror_name = sys.argv[1]
command = sys.argv[2:]

start_date = datetime.datetime.utcnow()

status = subprocess.run(command)

end_date = datetime.datetime.utcnow()

with lock:
    if not MIRROR_DATA.exists():
        data = {}
    else:
        with open(MIRROR_DATA, "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

    data.setdefault(
        mirror_name,
        {
            "description": "",
            "update-frequency": 0,
            "updates": [],
        }
    )
    data[mirror_name]["updates"].append({
        "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S"),
        "duration": (end_date - start_date).total_seconds(),
        "status": status.returncode,
    })

    with open(MIRROR_DATA, "w") as f:
        yaml.dump(data, f)
#    open("MIRROR_", "a").write("You were the chosen one.")
