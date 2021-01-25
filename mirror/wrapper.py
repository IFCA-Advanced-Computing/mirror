#!/usr/bin/python3

import datetime
import pathlib
import subprocess
import sys

path = pathlib.Path(__file__).parent / ".."  # noqa
path = path.resolve().as_posix()  # noqa
sys.path.append(path)  # noqa

import filelock
import yaml

import mirror

MIRROR_DATA = mirror.MIRROR_DATA
MIRROR_DATA_LOCK = mirror.MIRROR_DATA_LOCK

if len(sys.argv[1:]) < 2:
    print(f"ERROR: bad usage, use '{sys.argv[0]} <mirror_name> <command>'")
    sys.exit(1)

mirror_name = sys.argv[1]
command = sys.argv[2:]

MIRROR_LOCK = MIRROR_DATA_LOCK.parent / f"mirror-{mirror_name}.lock"

def do_sync(mirror_name, command):
    start_date = datetime.datetime.utcnow()

    status = subprocess.run(command)

    end_date = datetime.datetime.utcnow()

    data_lock = filelock.FileLock(MIRROR_DATA_LOCK, timeout=10)
    with data_lock:
        if not MIRROR_DATA.exists():
            data = {}
        else:
            with open(MIRROR_DATA, "r") as f:
                #data = yaml.load(f, Loader=yaml.FullLoader)
                data = yaml.safe_load(f)

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


try:
    mirror_lock = filelock.FileLock(MIRROR_LOCK)
    with mirror_lock.acquire(timeout=1):
        do_sync(mirror_name, command)
except filelock.Timeout:
    print(f"ERROR: cron job running or lock not released '{MIRROR_LOCK}'")
    sys.exit(1)
