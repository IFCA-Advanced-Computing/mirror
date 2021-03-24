#!/usr/bin/python3

import collections
import copy
import datetime
import os.path
import pathlib
import subprocess
import sys

path = pathlib.Path(__file__).parent / ".."  # noqa
path = path.resolve().as_posix()  # noqa
sys.path.append(path)  # noqa

import filelock
import jinja2
import yaml

import mirror

MIRROR_DATADIR = mirror.MIRROR_DATADIR
#MIRROR_DATA_LOCK = mirror.MIRROR_DATA_LOCK
ROOT = pathlib.Path(__file__).parent / ".."

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader((ROOT / 'template').as_posix()),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

outdir = ROOT / "output"

title = "IFCA repository mirror (repo.ifca.es)"
now = datetime.datetime.utcnow()
rundate = now.strftime("%Y-%m-%d %H:%M:%S")

uptime = subprocess.check_output(['uptime', "-p"]).decode("utf8")[3:].strip()


data = collections.OrderedDict()

files = list(MIRROR_DATADIR.glob("*yml"))
files.sort()

for f in files:
    MIRROR_DATA_LOCK = f.with_suffix(".lock")

    lock = filelock.FileLock(MIRROR_DATA_LOCK, timeout=10)

    with lock:
        if not f.exists():
            aux = {}
        else:
            with open(f, "r") as f:
                #aux = yaml.load(f, Loader=yaml.FullLoader)a
                aux = yaml.safe_load(f)
            aux = collections.OrderedDict(sorted(aux.items(), key=lambda t: t[0]))
    data.update(aux)

for m in data.values():
    m.setdefault("last ok", "N/A")
    m.setdefault("time ago", "N/A")
    m.setdefault("status", "outdated")

    updated = False
    for u in m["updates"][::-1]:
        if not u["status"] and not updated:
            m["last ok"] = u["end_date"]
            ago = now - datetime.datetime.strptime(u["end_date"], "%Y-%m-%d %H:%M:%S")
            ago = ago.total_seconds()
            m["time ago"] = "{:02.0f}:{:02.0f}:{:02.0f}".format(ago // 3600, (ago // 60) % 60, (ago % 60))
            if not m["update-frequency"]:
                m["status"] = "updated"
                updated = True
            else:
                last =  datetime.datetime.strptime(u["end_date"], "%Y-%m-%d %H:%M:%S")
                diff = now - last
                if diff.total_seconds() < (m["update-frequency"] * 60 * 60 * 1.25) + (15 * 60):
                    m["status"] = "updated"
                    updated = True
            break

        u["duration"] = "{:02.0f}:{:02.0f}:{:02.0f}".format(u["duration"] // 3600, (u["duration"] // 60) % 60, (u["duration"] % 60))


for t in ("index.html", "about.html", "stats.html"):
    with open(outdir / t, "w") as f:
        tpl = env.get_template(t)
        template_date = datetime.datetime.utcfromtimestamp(
            os.path.getmtime(tpl.filename)
        ).strftime("%Y-%m-%d %H:%M:%S")

        f.write(
            tpl.render(
                title=title,
                template_date=template_date,
                date=rundate,
                mirror_data=data,
                uptime=uptime,
            )
        )

tpl = env.get_template("stats_individual.html")
for mirror_name, mirror_data in data.items():
    with open(outdir / f"stats_{mirror_name}.html", "w") as f:
        f.write(
            tpl.render(
                title=title,
                template_date=template_date,
                date=rundate,
                mirror_data=mirror_data,
                mirror=mirror_name,
                uptime=uptime,
            )
        )
